#include <iostream>
#include <fstream>
#include <string>
#include <vector>

using namespace std;

int main(int argc, char* argv[]){
    string benchName (argv[1]); 
    ifstream inputs (benchName);
    vector<string> moduleList;
    if (inputs.is_open()){
        string line;
        while(inputs >> line){
            if( line == "Function:"){
                string ModuleName;
                inputs >> ModuleName;
                moduleList.push_back(ModuleName);
                ofstream module (ModuleName);
                if(module.is_open()){
                    string newLine = " ";
                    getline(inputs,newLine);
                    getline(inputs,newLine);
                    while( newLine != ""){
                        getline(inputs,newLine);
                        module << newLine << endl;
                    }
                }
                module.close();
            }
        }
    }
    inputs.close();
    ofstream output (benchName + ".modules");
    if(output.is_open()){
        for(vector<string>::iterator it = moduleList.begin(); it != moduleList.end(); ++it){
            output << *it << endl;
        }
    }
    output.close();
    return 0;
}
