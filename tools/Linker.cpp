#include <iostream>
#include <fstream>
#include <sstream>
#include <map>
#include <string>
#include <bitset>
#include <vector>
#include <sys/stat.h>
#include <unistd.h>

using namespace std;
bool debugLinker = false;

vector<string> callStack;

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

void addModule(map<string,bitset<32> >& moduleOpcodes, string newModule, bitset<32>& newModuleCode){
    if(moduleOpcodes.size() == 0) moduleOpcodes.insert(make_pair(newModule, newModuleCode));
    else if(moduleOpcodes.find(newModule) == moduleOpcodes.end()){
        newModuleCode = decrementBitset32(newModuleCode);
        moduleOpcodes.insert(make_pair(newModule,newModuleCode));
    }
}

void addOp(map<string,bitset<8> >& instOpcodes, string newInstruction, bitset<8>& newOp){
    if(instOpcodes.size() == 0) instOpcodes.insert(make_pair(newInstruction, newOp));
    else if(instOpcodes.find(newInstruction) == instOpcodes.end()){
        newOp = incrementBitset8(newOp);
        instOpcodes.insert(make_pair(newInstruction,newOp));
    }
}

void addQreg(map<string,bitset<16> >& qRegs, string qreg, bitset<16>& newReg){
    if(qRegs.size() == 0) qRegs.insert(make_pair(qreg, newReg));
    else if(qRegs.find(qreg) == qRegs.end()){
        newReg = incrementBitset16(newReg);
        qRegs.insert(make_pair(qreg,newReg));
    }
}
    
void printOpcodes(map<string,bitset<8> > instOpcodes){
    for(map<string,bitset<8> >::iterator it = instOpcodes.begin(); it != instOpcodes.end(); ++it){
        cout << it->first << " \t :: \t " << it->second.to_ulong() << endl;
    }
}

void printQregs(map<string,bitset<16> > qRegs){
    for(map<string,bitset<16> >::iterator it = qRegs.begin(); it != qRegs.end(); ++it){
        cout << it->first << " \t :: \t " << it->second.to_ulong() << endl;
    }
}

void linkLeaf(string& moduleName, map<string,bitset<8> >& instOpcodes, map<string,bitset<16> >& qRegs){ 
    string callStack(moduleName);
    string binaryOutput(callStack + ".bin");
    if (debugLinker) {
        cout << "Debug Info: " << endl << "module/input file name " << callStack << endl;
    }
    string line;
   
    ifstream CallStackFile (callStack.c_str());
    ofstream BinaryOutput (binaryOutput.c_str(), ios::out | ios::binary);
    if(CallStackFile.is_open() && BinaryOutput.is_open()){
        if(debugLinker){
            while(getline(CallStackFile,line)){
                cout << line << endl;
            }
        }
        int timeStep;
        char delim;
        int simdRegion;
        string instruction_or_schedts;
        string instruction;
        vector<string> qregs;
        string qreg1;
        string qreg2;
        string qreg3;

        bool movInst = false;
        bool cnotInst = false;
        bool toffInst = false;

        bitset<8> newOp(0ul);
        bitset<16> newqreg1(0ul);
        bitset<16> newqreg2(0ul);
        bitset<16> newqreg3(0ul);

        int dest;
        int src;
        int schedTS;
        char delim2;

        if(debugLinker) {
            cout << "Begin Module Processing" << endl;
        }

        while(CallStackFile >> timeStep >> delim >> simdRegion >> instruction_or_schedts ){
            if(debugLinker) cout << "Processing Next Line: " << endl;
            movInst = false;
            cnotInst = false;
            toffInst = false;
            qregs.clear();

            if (instruction_or_schedts == "MOV" || instruction_or_schedts == "BMOV" 
                || instruction_or_schedts == "TMOV"){
                movInst = true;
                instruction = instruction_or_schedts;
                CallStackFile >> dest >> src ;
                if(debugLinker) cout << "Found MOV Instruction" << endl;

            }
            else CallStackFile >> instruction;

            if(instruction == "CNOT") {
                CallStackFile >> qreg1 >> qreg2; 
                cnotInst = true;
                qregs.push_back(qreg1);
                qregs.push_back(qreg2);
                if(debugLinker) cout << "Found CNOT Instruction" << endl;
            }
            else if(instruction == "Toffoli") {
                CallStackFile >> qreg1 >> qreg2 >> qreg3;
                toffInst = true;
                qregs.push_back(qreg1);
                qregs.push_back(qreg2);
                qregs.push_back(qreg3);
                if(debugLinker) cout << "Found Toffoli Instruction" << endl;
            }
            else {
                CallStackFile >> qreg1;
                qregs.push_back(qreg1);
            }

            string fullInst = instruction;
            if(movInst) {
                if(debugLinker) cout << timeStep << "" << delim << "" << simdRegion << " " << instruction << " " << dest << " " << src << " " << qreg1 << endl;
                fullInst = instruction + to_string(dest) + to_string(src);
                addQreg(qRegs, qreg1, newqreg1); 
            }
            else if(cnotInst) {
                if(debugLinker) cout << timeStep << "" << delim << "" << simdRegion << " " << instruction << " " << qreg1 << " " << qreg2 << endl;
                addQreg(qRegs, qreg1, newqreg1); 
                addQreg(qRegs, qreg2, newqreg2); 
            }
            else if(toffInst) {
                if(debugLinker) cout << timeStep << "" << delim << "" << simdRegion << " " << instruction << " " << qreg1 << qreg2 << qreg3 << endl;
                addQreg(qRegs, qreg1, newqreg1); 
                addQreg(qRegs, qreg2, newqreg2); 
                addQreg(qRegs, qreg3, newqreg3); 
            }
            else {
                if(debugLinker) cout << timeStep << "" << delim << "" << simdRegion << " " << instruction << " " << qreg1 << endl;
            }
            addOp(instOpcodes, fullInst, newOp);
            if(debugLinker) {
                cout << "Now Adding:" << endl;
                cout << fullInst << " With Code: " << newOp << endl;
            }

            unsigned long op = instOpcodes.find(fullInst)->second.to_ulong();
            unsigned char opcode = static_cast<unsigned char>(op);
            BinaryOutput.write((char*) &opcode, sizeof(opcode));
            for(vector<string>::iterator vit = qregs.begin(); vit != qregs.end(); vit++){
                unsigned short qregister = qRegs.find(*vit)->second.to_ulong();
                BinaryOutput.write((char*) &qregister, sizeof(qregister));
            }
        }
    }
    CallStackFile.close();
    BinaryOutput.close();
}


void readMain(map<string,bitset<32> >& moduleOpcodes, map<string,bitset<8> >& instOpcodes, map<string,bitset<16> >& qRegs, vector<string>& moduleCalls, bitset<32>& newModuleCode){ 
    string main = "main";
    string main_bin = "main.bin";
    ifstream mainFile (main.c_str());
    ofstream mainOutput (main_bin.c_str(), ios::out | ios::binary);
    if(mainFile.is_open() && mainOutput.is_open()){
        string line;
        if(debugLinker){
            cout << "test: " << newModuleCode << endl;
            for(int i = 0; i < 64; i++) {
                newModuleCode = decrementBitset32(newModuleCode);
                cout << "test2: " << newModuleCode << endl;
            }
        }
        while(getline(mainFile,line)){
            if(line.find("llvm") == std::string::npos){
                istringstream ss(line);
                string module;
                ss >> module;
                std::size_t found = module.find(".");
                if(found != std::string::npos){
                    cout << module;
                    module = module.substr(0,found);
                    cout << module << endl;
                }
                moduleCalls.push_back(module);
                callStack.push_back(module);
                addModule(moduleOpcodes, module, newModuleCode);
                mainOutput.write((char*) &newModuleCode, sizeof(newModuleCode));
            }
        }
    }
}

void readModule(string& currModule, bitset<32>& newModuleCode, map<string,bitset<32> >& moduleCodes, map<string,bitset<8> >& instOpcodes, map<string,bitset<16> >& qRegs) {
    ifstream moduleFile (currModule.c_str());
    string outputFile = currModule + ".bin";
    ofstream moduleOutputFile (outputFile.c_str(), ios::out | ios::binary);
    if(moduleFile.is_open() && moduleOutputFile.is_open()){
        string line;
        while(getline(moduleFile,line)){
            istringstream ss(line);
            int timeStep;
            string module;
            if(ss >> timeStep) {
                linkLeaf(currModule,instOpcodes,qRegs); 
                break;
            }
            else {
                istringstream s(line);
                s >> module;
                if(module.find("llvm") == std::string::npos){
                    std::size_t found = module.find(".");
                    if(found != std::string::npos){
                        module = module.substr(0,found);
                    }
                    addModule(moduleCodes, module, newModuleCode);
                    moduleOutputFile.write((char*) &newModuleCode, sizeof(newModuleCode));
                    string filename = module + ".bin";
                    callStack.push_back(module);
                    if(!(file_exists(filename))){
                        readModule(module,newModuleCode,moduleCodes,instOpcodes,qRegs);    
                    }
                }
                else {} 
            }
        }
    }
}


int main( int argc, char* argv[] ){

    map<string, bitset<32> > moduleCodes;
    map<string, bitset<8> > instOpcodes;
    map<string, bitset<16> > qRegs;

    vector<string> moduleCalls;

    bitset<32> newModuleCode = (4294967295ul);
    readMain(moduleCodes, instOpcodes, qRegs, moduleCalls, newModuleCode);
    
    for(vector<string>::iterator it = moduleCalls.begin(); it != moduleCalls.end(); ++it){
        readModule((*it), newModuleCode, moduleCodes, instOpcodes, qRegs);
    }
    
    ofstream callStackFile ("main.calls.txt");
    for(vector<string>::iterator it = callStack.begin(); it != callStack.end(); ++it){
        callStackFile << *it << endl;
    }
    callStackFile.close();

    if(debugLinker){
        printOpcodes(instOpcodes);
        printQregs(qRegs);
    }

    return 0;
}
