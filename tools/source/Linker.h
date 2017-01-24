#ifndef LINKER_H 
#define LINKER_H 

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

using namespace std;

void addOp(map<string,bitset<8> >* instOpcodes, string newInstruction, bitset<8>* newOp);
void addQreg(map<string,bitset<16> >* qRegs, string qreg, bitset<16>* newReg);
void printOpcodes(map<string,bitset<8> >* instOpcodes);
void printQregs(map<string,bitset<16> >* qRegs);
void linkInstruction(string& instructionLine, map<string,bitset<8> >* instOpcodes, map<string,bitset<16> >* qRegs, ofstream& BinaryOutput);
void linkModule(string& moduleName, map<string,bitset<32> >* moduleOpcodes, map<string,bitset<8> >* instOpcodes, map<string,bitset<16> >* qRegs, vector<string>& moduleCalls, bitset<32>* newModuleCode, ofstream& callStack);
bool isIntrinsic(const string& name);
inline bool file_exists (const string& name);
bool addModule(map<string,bitset<32> >* moduleOpcodes, string newModule, bitset<32>* newModuleCode);

#endif
