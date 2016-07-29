#include <iostream>
#include <fstream>
#include <map>
#include <string>
#include <bitset>

using namespace std;
bool debugLinker = false;

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

void writeBinary(ofstream& BinaryOutput, map<string,bitset<8> > instOpcodes, map<string,bitset<16> > qRegs){
    char x[8];
    BinaryOutput.write(x, sizeof(x));
}

void readModule(const char* moduleName, map<string,bitset<8> >& instOpcodes, map<string,bitset<16> >& qRegs){ 
    string callStack(moduleName);
    string binaryOutput(callStack + ".bin");
    if (debugLinker) {
        cout << "Debug Info: 1. module name: " << callStack << endl;
    }
    string line;
   
    ifstream CallStackFile (callStack);
    ofstream BinaryOutput (binaryOutput, ios::out | ios::binary);
    if(CallStackFile.is_open() && BinaryOutput.is_open()){
        int timeStep;
        char delim;
        int simdRegion;
        string instruction_or_schedts;
        string instruction;
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

        while(CallStackFile >> timeStep >> delim >> simdRegion >> instruction_or_schedts ){
            movInst = false;
            cnotInst = false;
            toffInst = false;
            if (instruction_or_schedts == "MOV"){
                movInst = true;
                instruction = instruction_or_schedts;
                CallStackFile >> dest >> src ;
            }
            else CallStackFile >> instruction;

            if(instruction == "CNOT") {
                CallStackFile >> qreg1 >> qreg2; 
                cnotInst = true;
            }
            else if(instruction == "Toffoli") {
                CallStackFile >> qreg1 >> qreg2 >> qreg3;
                toffInst = true;
            }
            else CallStackFile >> qreg1;

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
            writeBinary(BinaryOutput, instOpcodes, qRegs);
        }
    }
    CallStackFile.close();
}

int main( int argc, char* argv[] ){
    if (argc < 2){
        cout << "Too few parameters specified" << endl;
        cout << "Usage: [module name]" << endl;
        exit(1);
    }

    map<string, bitset<8> > instOpcodes;
    map<string, bitset<16> > qRegs;

    readModule(argv[1], instOpcodes, qRegs);

    if(debugLinker){
        printOpcodes(instOpcodes);
        printQregs(qRegs);
    }

    return 0;
}
