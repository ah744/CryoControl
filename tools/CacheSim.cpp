#include <iostream>
#include <fstream>
#include <algorithm>
#include <string>
#include <map>
#include <vector>
#include <deque>

using namespace std;

bool debugCacheSim = false;

struct CryoCache {
    int capacity;
    const char* associativity;
    const char* eviction;
    int used_memory;
    int numDecompressions;
    int numRecompressions;
    int numHits;
    int numMisses;
    vector<string> vectCalls;
    deque<string> cacheContents;
    map<string,int> modSizes;
	map<string,int> decompressionMap;
	map<string,int> decompressionRequirementsMap;
    CryoCache():capacity(1024),associativity("full"),eviction("LRU"),used_memory(0),numHits(0),numMisses(0),numDecompressions(0),numRecompressions(0) { }
};

void initializeCache(CryoCache& cache, int input_cap, char* input_associativity, char* input_eviction){
    cache.capacity = input_cap;
    cache.associativity = input_associativity;
    cache.eviction = input_eviction;

}

void readBenchmark(CryoCache& cache, const char* benchName){
    string bName(benchName);
    string moduleSizes = bName + "sizes.txt";
    string callStack = bName + "calls.txt";
	string decompressionRequirements = bName + "decomp.sizes.txt";
    if (debugCacheSim) {
        cout << "Debug Info: 1. benchmark name: " << bName << " 2. module sizes file: "
             << moduleSizes << " 3. call stack file: " << callStack << endl;
    }
    string line;
    ifstream moduleSizeFile (moduleSizes);
    if (moduleSizeFile.is_open()){
        string name;
        int size;
        while(moduleSizeFile >> name >> size){
            cache.modSizes.insert(make_pair(name,size));
			cache.decompressionMap.insert(make_pair(name,0));
        }
    }
    moduleSizeFile.close();

	ifstream decompSizes (decompressionRequirements);
    if (decompSizes.is_open()){
        string name;
        int size;
        while(decompSizes >> name >> size){
            cache.decompressionRequirementsMap.insert(make_pair(name,size));
        }
    }
    decompSizes.close();

    ifstream CallStackFile (callStack);
    if(CallStackFile.is_open()){
        string callInstruction;
        while(CallStackFile >> callInstruction)
            cache.vectCalls.push_back(callInstruction);
    }
    CallStackFile.close();

    if(debugCacheSim){
        cout << "Module Sizes:" << endl;
        for(map<string,int>::iterator it = cache.modSizes.begin(); it != cache.modSizes.end(); ++it)
            cout << it->first << ":" << it->second << endl;
        cout << "Call Instructions:" << endl;
        for(vector<string>::iterator it = cache.vectCalls.begin(); it != cache.vectCalls.end(); ++it)
            cout << *it << endl;
		cout << "Decompression Requirements by Module:" << endl;
        for(map<string,int>::iterator it = cache.decompressionRequirementsMap.begin(); it != cache.decompressionRequirementsMap.end(); ++it)
            cout << it->first << ":" << it->second << endl;
    }
}


void printCacheContents(CryoCache cache){
    cout << "#### Current Cache Contents: " << endl;
    cout << "Number of Modules: " << cache.cacheContents.size() << endl;
    for(deque<string>::iterator it = cache.cacheContents.begin(); it != cache.cacheContents.end(); ++it)
        cout << *it << endl;
    cout << "#### End of Cache Contents" << endl;
}

bool fillCache(CryoCache& cache, int instSize, int decompressionSize, string curInst){
    if(debugCacheSim){
        cout << "Current Free Memory: " << cache.capacity - cache.used_memory << endl;
        cout << "Filling With Instruction: " << curInst << " of size: " << instSize << endl;
    }

    if (instSize + cache.used_memory + decompressionSize<= cache.capacity){
        cache.used_memory += instSize;
        cache.cacheContents.push_back(curInst);
        cache.numDecompressions++;
		cache.decompressionMap[curInst]++;

        if(debugCacheSim){
            cout << "Success" << endl;
            cout << "New Free Memory: " << cache.capacity - cache.used_memory;
        }
        return true;
    }
    return false;
}

void runCache(CryoCache& cache){
    for(vector<string>::iterator inst = cache.vectCalls.begin(); inst != cache.vectCalls.end(); ++inst){
        string currentInstruction = *inst;
        int instructionSize = cache.modSizes.find(*inst)->second;
		int decompressionSize = cache.decompressionRequirementsMap.find(*inst)->second;
        if ( find(cache.cacheContents.begin(), cache.cacheContents.end(), currentInstruction) == cache.cacheContents.end() ) {
            while( !fillCache(cache, instructionSize, decompressionSize, currentInstruction) ){
                if (string(cache.eviction) == "FIFO") {
                    string victimInstruction = cache.cacheContents.front();
                    int victimSize = cache.modSizes.find(victimInstruction)->second;
                    cache.cacheContents.pop_front();
                    cache.used_memory -= victimSize;
                    cache.numRecompressions++;
                    if (debugCacheSim){
                        cout << "Eviction" <<endl;
                        cout << "Free Memory: " << cache.capacity - cache.used_memory;
                    }
                }
            }
            cache.numMisses++;
        }
        else {
            cache.numHits++;
            if (debugCacheSim) cout << "Cache Hit: " << currentInstruction << endl;
        }
    }
}

void printStatistics(CryoCache cache, const char* benchName, int workflowIntegrate){
    if(workflowIntegrate == 0){
        cout << "------- Cryogenic Control Module Statistics ----------" << endl;
        cout << "Benchmark: " << benchName << endl;
        cout << "Size of Cache: " << cache.capacity << endl;
        cout << "Cache associativity: " << cache.associativity << endl;
        cout << "Cache eviction policy: " << cache.eviction << endl;
        cout << "Number of modules run: " << cache.vectCalls.size() << endl;
        cout << "Number of module decompressions: " << cache.numDecompressions << endl;
        cout << "Number of module recompressions: " << cache.numRecompressions << endl;
        cout << "Number of cache hits: " << cache.numHits << endl;
        cout << "Number of cache misses: " << cache.numMisses << endl;

		for(map<string,int>::iterator it = cache.decompressionMap.begin(); it!=cache.decompressionMap.end();++it){
			cout << it->first << " " << it->second << endl;
		}
    }
    else if(workflowIntegrate == 1){ 
        cout << cache.numDecompressions << endl;
		for(map<string,int>::iterator it = cache.decompressionMap.begin(); it!=cache.decompressionMap.end();++it){
			cout << it->first << ":" << it->second << endl;
		}

    }
}

int main( int argc, char *argv[]){
    if (argc < 6){
        cout << "Error: Too Few Parameters Specified" << endl;
        cout << "Usage: " << "[cache capacity] [cache associativity] [eviction policy] [benchmark name] [workflow printing] " << endl;
        exit(1);
    }
    CryoCache cache;
    int in_cap = atoi(argv[1]);
    initializeCache(cache, in_cap, argv[2], argv[3]);
    readBenchmark(cache, argv[4]);
    runCache(cache);
    printStatistics(cache, argv[4], atoi(argv[5]));
    return 0;
}
