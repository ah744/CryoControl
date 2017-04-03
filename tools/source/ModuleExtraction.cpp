#include <iostream>
#include <sstream>
#include <fstream>
#include <algorithm>
#include <string>
#include <vector>

using namespace std;

void addToModules(vector<string>& modules, string& moduleName){
    if( find(modules.begin(),modules.end(),moduleName) == modules.end() ){
        modules.push_back(moduleName);
    }
}

void readModuleFile(ifstream& inputs, vector<string>& modules, bool isCG){
    if(inputs.is_open()){
        string line;
        while(getline(inputs,line)){
            if( line.find("Function:") != std::string::npos) {
                string ModuleName;
                string func;
                istringstream s(line);
                s >> func >> ModuleName;
                addToModules(modules,ModuleName);
                ofstream outputModule;
				outputModule.open(ModuleName.c_str());
                if(outputModule.is_open()){
                    string newLine = " ";
					getline(inputs,newLine);
                        while(getline(inputs,newLine) && !(newLine.empty())){
                            if((newLine.find("LPFS") == std::string::npos) && 
							  (newLine.find("Num") == std::string::npos)){
								outputModule << newLine << endl;
							}
                        }
                	outputModule.close();
                }
				else{
					cout << "Error: Could not open module output file\n";
				}
            }
        }
    }
    inputs.close();
}

int main(int argc, char* argv[]){
    if(argc < 2){
        cout << "Too few parameters specified." << endl;
        cout << "Usage: moduleextraction <benchmark>" << endl;
        exit(1);
    }
    string benchName (argv[1]); 
    string benchLPFSName = benchName + "lpfs";
    ifstream inputs_cg (benchLPFSName.c_str()); 
    vector<string> moduleList;
    readModuleFile(inputs_cg,moduleList,true);
//    inputs_cg.close();
//    ifstream inputs_lpfs (benchLPFSName.c_str());
//    readModuleFile(inputs_lpfs,moduleList,false);
    inputs_cg.close();
//    inputs_lpfs.close();
    string benchOutputName = benchName + "modules";
    ofstream output (benchOutputName.c_str());
    if(output.is_open()){
        for(vector<string>::iterator it = moduleList.begin(); it != moduleList.end(); ++it){
            output << *it << endl;
        }
    }
    output.close();
    return 0;
}
