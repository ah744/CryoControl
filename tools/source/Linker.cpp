#include <iostream>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <map>
#include <string>
#include <bitset>
#include <vector>
#include <sys/stat.h>
#include <unistd.h>
#include "Linker.h"

#define LINE_SIZE 40 //bits
#define BLOCK_SIZE 120 //bits 

using namespace std;

bool debugLinker = false;

vector<string> callStack;
vector<string> leafModules;

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
		name == "Rz"		)
		return true;
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

bool addModule(map<string,bitset<32> >* moduleOpcodes, string newModule, bitset<32>* newModuleCode){
    if(moduleOpcodes->size() == 0) {
		moduleOpcodes->insert(make_pair(newModule, (*newModuleCode)));
		return true;
	}
    else if(moduleOpcodes->find(newModule) == moduleOpcodes->end()){
        (*newModuleCode) = decrementBitset32(*newModuleCode);
        moduleOpcodes->insert(make_pair(newModule,(*newModuleCode)));
		return true;
    }
	return false;
}

void addOp(map<string,bitset<8> >* instOpcodes, string newInstruction, bitset<8>* newOp){
    if(instOpcodes->size() == 0){
	   	instOpcodes->insert(make_pair(newInstruction, (*newOp)));
	}
    else if(instOpcodes->find(newInstruction) == instOpcodes->end()){
        (*newOp) = incrementBitset8(*newOp);
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
    
void printOpcodes(map<string,bitset<8> >* instOpcodes){
    for(map<string,bitset<8> >::iterator it = instOpcodes->begin(); it != instOpcodes->end(); ++it){
        cout << it->first << " \t :: \t " << it->second.to_ulong() << endl;
    }
}

void printQregs(map<string,bitset<16> >* qRegs){
    for(map<string,bitset<16> >::iterator it = qRegs->begin(); it != qRegs->end(); ++it){
        cout << it->first << " \t :: \t " << it->second.to_ulong() << endl;
    }
}

void linkInstruction(string& instructionLine, map<string,bitset<8> >* instOpcodes, map<string,bitset<16> >* qRegs, ofstream& BinaryOutput){ 
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
	    bitset<8> newOp(0ul);
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
	    unsigned char opcode = static_cast<unsigned char>(op);
	    BinaryOutput.write((char*) &opcode, sizeof(opcode));
		if(qregs.size() < 2) qregs.push_back((*qregs.begin())); // Pad each line to 5 bytes for indexing
	    for(vector<string>::iterator vit = qregs.begin(); vit != qregs.end(); vit++){
	        unsigned short qregister = qRegs->find(*vit)->second.to_ulong();
	        BinaryOutput.write((char*) &qregister, sizeof(qregister));
	    }
	}
}

void linkModule(string& moduleName, map<string,bitset<32> >* moduleOpcodes, map<string,bitset<8> >* instOpcodes, map<string,bitset<16> >* qRegs, vector<string>& moduleCalls, bitset<32>* newModuleCode, ofstream& callStack){ 
	ifstream moduleFile(moduleName.c_str());
	string moduleOutputFilename = moduleName + ".bin";
	//TODO add module naming here, spliced by block size
	ofstream moduleOutputFile(moduleOutputFilename.c_str(), ios::out | ios::app);
	int pc = 1;
	if(moduleFile.is_open() && moduleOutputFile.is_open()){
		int ts,simd;
		char delim;
		string instruction;
		string line;
		while(getline(moduleFile,line)){
	    	istringstream ss(line);
	    	ss >> ts >> delim >> simd >> instruction;
			if(!(isIntrinsic(instruction))){
				callStack << pc++ << "-" << moduleName<< "\n";
	    		if(addModule(moduleOpcodes, instruction, newModuleCode)){
					linkModule(instruction, moduleOpcodes, instOpcodes, qRegs, moduleCalls, newModuleCode, callStack);
				}
				moduleOutputFile.write((char*) newModuleCode, sizeof(*newModuleCode));

		   	}
			else{
				linkInstruction(line, instOpcodes, qRegs, moduleOutputFile);
			}
		}
		callStack << pc << "-" << moduleName<< "\n";
	}
	moduleFile.close();
}

int main( int argc, char* argv[] ){
    map<string, bitset<32> >* moduleCodes = new map<string, bitset<32> >;
    map<string, bitset<8> >* instOpcodes = new map<string, bitset<8> >;
    map<string, bitset<16> >* qRegs = new map<string,bitset<16> >;
    vector<string> moduleCalls;
    bitset<32> newModuleCode = (4294967295ul);
	string main = "main";
	ofstream callStackFile ("main.calls.txt", ios::out | ios::app);
	linkModule(main, moduleCodes, instOpcodes, qRegs, moduleCalls, &newModuleCode, callStackFile);
    if(debugLinker){
        printOpcodes(instOpcodes);
        printQregs(qRegs);
    }
    return 0;
}
