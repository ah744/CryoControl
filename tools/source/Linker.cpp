#include <iostream>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <map>
#include <string>
#include <bitset>
#include <vector>
#include <sys/stat.h>
#include <math.h>
#include <unistd.h>
#include "Linker.h"

#define LINE_SIZE 64 //bits
#define LINE_SIZE_BYTES 8 //bits
#define BLOCK_SIZE 1024 //bits 
#define ROTATION_FLAG true 

using namespace std;

bool debugLinker = false;

vector<string> callStack;
vector<string> leafModules;
vector<string> rotationQubits;
unsigned long long CodeSize;
unsigned long long InstructionCount;
unsigned long long RotationInstCount;


bool isIntrinsic(const string& name){
	if(name == "CNOT" 		||
		name == "X"			||		
		name == "PrepZ"		||
		name == "H"			||
		name == "Sdag"		||
		name == "Tdag"		||
		name == "Y"			||
		name == "Z"			||
		name == "S"			||
		name == "T"			||
		name == "MeasX"		||
		name == "MeasZ"		||
		name == "Fredkin"	||
		name == "BEGIN_ROT"	||
		name == "END_ROT"	||
		name == "rot.T" 	||
		name == "rot.Tdag" 	||
		name == "rot.S" 	||
		name == "rot.Sdag" 	||
		name == "rot.H" 	||
		name == "rot.X" 	||
		name == "rot.Y" 	||
		name == "rot.Z" 	||
		name == "Rz"		)
		return true;
	return false;	
}

bool isBeginRotSequence(const string& name){
	if(name == "BEGIN_ROT") return true;
	return false;
}
bool isEndRotSequence(const string& name){
	if(name == "END_ROT") return true;
	return false;
}

inline bool file_exists (const string& name){
    struct stat buffer;
    return (stat (name.c_str(), &buffer) == 0);
}

bitset<8> incrementBitset8(bitset<8> code){
    unsigned long num = code.to_ulong();
    num++;
    bitset<8> newOp(num);
    return newOp;
} 

bitset<16> incrementBitset16(bitset<16> code){
    unsigned long num = code.to_ulong();
    num++;
    bitset<16> newOp(num);
    return newOp;
}

bitset<32> decrementBitset32(bitset<32> code){
    unsigned long num = code.to_ulong();
    num--;
    bitset<32> newOp(num);
    return newOp;
}

bitset<64> decrementBitset64(bitset<64> code){
    unsigned long num = code.to_ulong();
    num--;
    bitset<64> newOp(num);
    return newOp;
}

bool addModule(map<string,bitset<64> >* moduleOpcodes, string newModule, bitset<64>* newModuleCode){
    if(moduleOpcodes->size() == 0) {
		moduleOpcodes->insert(make_pair(newModule, (*newModuleCode)));
		return true;
	}
    else if(moduleOpcodes->find(newModule) == moduleOpcodes->end()){
        (*newModuleCode) = decrementBitset64(*newModuleCode);
        moduleOpcodes->insert(make_pair(newModule,(*newModuleCode)));
		return true;
    }
	return false;
}

void addOp(map<string,bitset<32> >* instOpcodes, string newInstruction, bitset<32>* newOp){
    if(instOpcodes->size() == 0){
	   	instOpcodes->insert(make_pair(newInstruction, (*newOp)));
	}
    else if(instOpcodes->find(newInstruction) == instOpcodes->end()){
        (*newOp) = decrementBitset32(*newOp);
        instOpcodes->insert(make_pair(newInstruction,(*newOp)));
    }
	else{
		(*newOp) = instOpcodes->find(newInstruction)->second;
	}
}

void addQreg(map<string,bitset<16> >* qRegs, string qreg, bitset<16>* newReg){
    if(qRegs->size() == 0) qRegs->insert(make_pair(qreg, (*newReg)));
    else if(qRegs->find(qreg) == qRegs->end()){
        (*newReg) = incrementBitset16(*newReg);
        qRegs->insert(make_pair(qreg,(*newReg)));
    }
	else (*newReg) = qRegs->find(qreg)->second;
}
    
void printOpcodes(map<string,bitset<32> >* instOpcodes){
    for(map<string,bitset<32> >::iterator it = instOpcodes->begin(); it != instOpcodes->end(); ++it){
        cout << it->first << " \t :: \t " << it->second.to_ulong() << endl;
    }
}

void printQregs(map<string,bitset<16> >* qRegs){
    for(map<string,bitset<16> >::iterator it = qRegs->begin(); it != qRegs->end(); ++it){
        cout << it->first << " \t :: \t " << it->second.to_ulong() << endl;
    }
}

void linkInstruction(string& instructionLine, map<string,bitset<32> >* instOpcodes, map<string,bitset<16> >* qRegs, ofstream& BinaryOutput){ 
	if(BinaryOutput.is_open()){
	    int timeStep;
	    char delim;
	    int simdRegion;
	    string instruction;
	    vector<string> qregs;
	    string qreg1;
	    string qreg2;
	    string qreg3;
	    bool cnotInst = false;
	    bool toffInst = false;
	    bitset<32> newOp(0ul);
	    bitset<16> newqreg1(0ul);
		vector<bitset<16> > newqregs;
	    int dest;
	    int src;
	    int schedTS;
	    char delim2;
		int numArgs = 1;
	    istringstream ss(instructionLine);
	    ss >> timeStep >> delim >> simdRegion >> instruction;
		if(instruction == "CNOT") numArgs = 2;
		else if(instruction == "Toffoli") numArgs = 3;
		for(int i = 0; i < numArgs; i++){
			ss >> qreg1;
			qregs.push_back(qreg1);
			addQreg(qRegs, qreg1, &newqreg1);
			newqregs.push_back(newqreg1);
		}
	    addOp(instOpcodes, instruction, &newOp);
	
	    unsigned long op = instOpcodes->find(instruction)->second.to_ulong();
	    unsigned int opcode = static_cast<unsigned int>(op);
	    BinaryOutput.write((char*) &opcode, sizeof(opcode));
		if(qregs.size() < 2) qregs.push_back((*qregs.begin())); // Pad each line to 5 bytes for indexing
	    for(vector<string>::iterator vit = qregs.begin(); vit != qregs.end(); vit++){
	        unsigned short qregister = qRegs->find(*vit)->second.to_ulong();
	        BinaryOutput.write((char*) &qregister, sizeof(qregister));
	    }
	}
}

void linkRotationInstruction(string& instruction, map<string,bitset<32> >* instOpcodes, ofstream& moduleOutputFile){
	if(moduleOutputFile.is_open()){
		int timeStep;
		char delim;
		int simdRegion;
		string instruction;
	    bitset<32> newOp(0ul);
		istringstream ss(instruction);
		ss >> timeStep >> delim >> simdRegion >> instruction;
	    addOp(instOpcodes, instruction, &newOp);
	    unsigned long op = instOpcodes->find(instruction)->second.to_ulong();
	    unsigned char opcode = static_cast<unsigned char>(op);
	    moduleOutputFile.write((char*) &opcode, sizeof(opcode));
	}
	else exit(1);
}

void linkRotationInstructionStats(string& line){
	int timeStep;
	char delim;
	int simdRegion;
	string qubit;
	string instruction;
	bitset<32> newOp(0ul);
	istringstream ss(line);
	ss >> timeStep >> delim >> simdRegion >> instruction >> qubit;
	if(std::find(rotationQubits.begin(), rotationQubits.end(), qubit) != rotationQubits.end()){
		rotationQubits.push_back(qubit);
	}
	RotationInstCount++;
}

void linkModuleStats(string& moduleName, map<string,bitset<64> >* moduleOpcodes, bitset<64>* newModuleCode, ofstream& callStack, bool rotationFlag){ 
	ifstream moduleFile(moduleName.c_str());
	if(moduleFile.is_open()){
		int ts,simd;
		char delim;
		int index; 
		bool newMod = false;
		string instruction;
		string line;
		callStack << moduleName<< "\n";
		while(getline(moduleFile,line)){
	    	istringstream ss(line);
	    	ss >> ts >> delim >> simd >> instruction;
			if(!(isIntrinsic(instruction))) {
				CodeSize += LINE_SIZE_BYTES;
				InstructionCount++;
				newMod = addModule(moduleOpcodes, instruction, newModuleCode);
				if(newMod) linkModuleStats(instruction, moduleOpcodes, newModuleCode, callStack, rotationFlag);
				else callStack << instruction << "\n";
				callStack << moduleName << "\n";
			}
			else if(rotationFlag && instruction.find("BEGIN_ROT") != std::string::npos){
				CodeSize += LINE_SIZE_BYTES;
				InstructionCount++;
				while(getline(moduleFile, line) && line.find("END_ROT") == std::string::npos){
					linkRotationInstructionStats(line);
				}
				if(instruction.find("END_ROT") == std::string::npos){
					CodeSize += LINE_SIZE_BYTES;
					InstructionCount++;
					int numQubits = rotationQubits.size();
					double numBits = ceil(log2(numQubits));
					CodeSize += (32 + numBits) * RotationInstCount;
					return;
				}
			}
			else {
				CodeSize += LINE_SIZE_BYTES;
				InstructionCount++;	
			}
		}
	}
	moduleFile.close();
}

void linkModule(string& moduleName, map<string,bitset<64> >* moduleOpcodes, map<string,bitset<32> >* instOpcodes, map<string,bitset<16> >* qRegs, vector<string>& moduleCalls, bitset<64>* newModuleCode, ofstream& callStack, bool newModule, bool rotationFlag){ 
	ifstream moduleFile(moduleName.c_str());
	int numLines = BLOCK_SIZE/LINE_SIZE;
	int moduleBlockNumber = 0;
	int terminate = 0;
	bool newMod = false;
	int lineNumber = 0;
	if(moduleFile.is_open()){
		int ts,simd;
		char delim;
		int index; 
		string instruction;
		string line;
		callStack << moduleBlockNumber << "-" << moduleName<< "\n";
		while(getline(moduleFile,line)){
			string moduleOutputFilename = to_string(moduleBlockNumber) + "-" + moduleName + ".bin";
			ofstream moduleOutputFile(moduleOutputFilename.c_str(), ios::out | ios::binary | ios::app);
			if(moduleOutputFile.is_open()){
	    		istringstream ss(line);
	    		ss >> ts >> delim >> simd >> instruction;
				if(!(isIntrinsic(instruction))){
	    			newMod = addModule(moduleOpcodes, instruction, newModuleCode);
					linkModule(instruction, moduleOpcodes, instOpcodes, qRegs, moduleCalls, newModuleCode, callStack, newMod, rotationFlag);
					if(newModule) moduleOutputFile.write((char*) newModuleCode, sizeof(*newModuleCode));
					callStack << moduleBlockNumber << "-" << moduleName<< "\n";
		   		}
				else if(rotationFlag && instruction.find("rot.") != std::string::npos){
					callStack << "Found rot inst \n";
					linkRotationInstruction(line, instOpcodes, moduleOutputFile);
				}	
/*				else if(isBeginRotSequence(instruction) && rotationFlag){
					linkInstruction(line, instOpcodes, qRegs, moduleOutputFile);
					terminate++;
					while(terminate != 0){
						if(getline(moduleFile,line)){
	    					istringstream ss(line);
	    					ss >> ts >> delim >> simd >> instruction;
							if(instruction == "END_ROT"){
								terminate--;
								linkInstruction(line, instOpcodes, qRegs, moduleOutputFile);
							}
							else{
								linkRotationInstruction(line, instOpcodes, moduleOutputFile); 
							}
						}
					}
				}*/
				else if(newModule){
					linkInstruction(line, instOpcodes, qRegs, moduleOutputFile);
				}
			}
			moduleOutputFile.close();
			lineNumber++;
			int lastBlock = moduleBlockNumber;
			moduleBlockNumber = lineNumber/numLines;
			if(lastBlock != moduleBlockNumber){
				callStack << moduleBlockNumber << "-" << moduleName << "\n";
			}
		}
	}
	moduleFile.close();
}

int main( int argc, char* argv[] ){
    map<string, bitset<64> >* moduleCodes = new map<string, bitset<64> >;
    map<string, bitset<64> >* moduleCodes2 = new map<string, bitset<64> >;
    map<string, bitset<32> >* instOpcodes = new map<string, bitset<32> >;
    map<string, bitset<16> >* qRegs = new map<string,bitset<16> >;
    vector<string> moduleCalls;
    bitset<64> newModuleCode = (4294967295ul);
    bitset<64> newModuleCode2 = (4294967295ul);
	string main = "main";
	CodeSize = 0;
	InstructionCount = 0;
	ofstream callStackFile ("main.calls.txt", ios::out | ios::app);
	ofstream callStackFile2 ("main.stats.txt", ios::out | ios::app);
	ofstream codeSize ("codesize.txt", ios::out | ios::app);
	linkModule(main, moduleCodes, instOpcodes, qRegs, moduleCalls, &newModuleCode, callStackFile, true, ROTATION_FLAG);
	linkModuleStats(main, moduleCodes2, &newModuleCode2, callStackFile2, ROTATION_FLAG);
	codeSize << CodeSize << " bytes \n";
	codeSize << InstructionCount << " instructions\n";
	codeSize.close();
	callStackFile.close();
    if(debugLinker){
        printOpcodes(instOpcodes);
        printQregs(qRegs);
    }
    return 0;
}
