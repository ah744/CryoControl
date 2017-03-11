#include <iostream>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <string>
#include <map>
#include <vector>
#include <deque>
#include <string>
#include <bitset>
#include <math.h>
#include <sys/stat.h>
#include <unistd.h>

#include "Linker.h"

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
	int numEvictions;
    vector<string> vectCalls;
    vector<string> victimList;
    deque<string> cacheContents;
    map<string,int> callFrequency;
    map<string,deque<int> > nextUse;
    map<string,int> modSizes;
	map<string,int> decompressionMap;
	map<string,int> decompressionRequirementsMap;
    CryoCache():capacity(1024),associativity("full"),eviction("FIFO"),used_memory(0),numHits(0),numMisses(0),numEvictions(0),numDecompressions(0),numRecompressions(0) { }
};

void initializeCache(CryoCache& cache, int input_cap, char* input_associativity, char* input_eviction){
    cache.capacity = input_cap;
    cache.associativity = input_associativity;
    cache.eviction = input_eviction;
}

void readBenchmark(CryoCache& cache, const char* benchName, int cache_flag){
	string bName(benchName);
    string moduleSizes = bName + "sizes.txt";
    string callStack = bName + "calls.txt";
    string callFrequencyFile = "call_frequency.txt";
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
   	ifstream callFreqFile (callFrequencyFile);
    if (callFreqFile.is_open()){
    	string name;
        int frequency;
        while(callFreqFile >> name >> frequency){
            cache.callFrequency.insert(make_pair(name,frequency));
        }
    }
    ifstream CallStackFile (callStack);
    if(CallStackFile.is_open()){
        string callInstruction;
        while(CallStackFile >> callInstruction){
            cache.vectCalls.push_back(callInstruction);
            if ( cache.nextUse.find(callInstruction) == cache.nextUse.end()){
                cache.nextUse[callInstruction] = {}; 
            }
            cache.nextUse[callInstruction].push_back(cache.vectCalls.size());
        }
        if (debugCacheSim){
            for(map<string,deque<int> >::iterator it = cache.nextUse.begin(); it != cache.nextUse.end(); ++it){
                cout << it->first << " ";
                for(deque<int>:: iterator sit = it->second.begin(); sit != it->second.end(); ++sit){
                    cout << (*sit) << " ";
                }
                cout << endl;
            }
        }
    }
    CallStackFile.close();
    if(debugCacheSim){
        cout << "Module Sizes:" << endl;
        for(map<string,int>::iterator it = cache.modSizes.begin(); it != cache.modSizes.end(); ++it)
            cout << it->first << ":" << it->second << endl;
        cout << "Call Instructions:" << endl;
        for(vector<string>::iterator it = cache.vectCalls.begin(); it != cache.vectCalls.end(); ++it)
            cout << *it << endl;
        for(map<string,int>::iterator it = cache.callFrequency.begin(); it != cache.callFrequency.end(); ++it)
            cout << it->first << ":"<<it->second<<endl;
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

void evict(CryoCache& cache){
	if (string(cache.eviction) == "FIFO") {
	    string victimInstruction = cache.cacheContents.front();
	    int victimSize = cache.modSizes.find(victimInstruction)->second;
	    cache.cacheContents.pop_front();
	    cache.used_memory -= victimSize;
		if (cache.used_memory < 0) cache.used_memory = 0;
	    cache.numRecompressions++;
	    if (debugCacheSim){
	        cout << "Eviction: " << victimInstruction << endl;
	        cout << "Free Memory: " << cache.capacity - cache.used_memory;
	    }
	}
	if (string(cache.eviction) == "LIFO") {
	    string victimInstruction = cache.cacheContents.back();
	    int victimSize = cache.modSizes.find(victimInstruction)->second;
	    cache.cacheContents.pop_back();
	    cache.used_memory -= victimSize;
		if (cache.used_memory < 0) cache.used_memory = 0;
	    cache.numRecompressions++;
	    if (debugCacheSim){
	        cout << "Eviction" <<endl;
	        cout << "Free Memory: " << cache.capacity - cache.used_memory;
	    }
	}
}

void evict_NextUse(CryoCache& cache, int currentIndex){
    if (debugCacheSim) {
        cout << "Current Index: " << currentIndex << endl;
        cout << "Cache size: " << cache.cacheContents.size() << endl;
		cout << "---- Cache Contents -----\n";
		for(deque<string>::iterator it = cache.cacheContents.begin(); it != cache.cacheContents.end(); it++)
			cout << "\t" << (*it) << endl;
    }
    int max = 0;
    string victim = cache.cacheContents.back();
    bool performedEviction = false;
    if (cache.cacheContents.size() < 2) {
        cache.cacheContents.clear();
        performedEviction = true;
    }
    else {
        for(deque<string>::reverse_iterator rin = cache.cacheContents.rbegin(); rin != cache.cacheContents.rend(); rin++){
            if (debugCacheSim) cout << "Checking cache content: " << (*rin) << ":" << cache.nextUse[(*rin)].front() << endl;
            map<string,deque<int> >::iterator it = cache.nextUse.find(*rin);
            int newValue;
            if ((it != cache.nextUse.end()) && it->second.empty()) newValue = INT_MAX;
            else newValue = it->second.front();
            if (newValue == 0){
                victim = it->first;
                break;
            }
            if (it != cache.nextUse.end() && newValue > max){
                max = newValue;
                victim = it->first;
            }
        }
        if (debugCacheSim){
            cout << "Found victim: " << victim << endl;
        }
        if (!cache.cacheContents.empty()) {
			int victimSize = cache.modSizes.find(victim)->second;
			cache.cacheContents.erase(remove(cache.cacheContents.begin(),cache.cacheContents.end(),victim),cache.cacheContents.end());
			cache.used_memory -= victimSize;
			cache.numEvictions++;
			if (debugCacheSim) {
				cout << "Evicted: " << victim << endl;
				cout << "Num Evictions: " << cache.numEvictions << endl;
			}
		}
//        for(deque<string>::iterator it = cache.cacheContents.begin(); it != cache.cacheContents.end();it++){
//            cout << "Looking for " << (*it) << endl;
//            if ((*it) == victim){
//                cout << "found it!\n";
//                cache.cacheContents.erase(it);
//                performedEviction = true;
//            }
//        }
    }
    if (performedEviction){
        if(debugCacheSim) cout << "Evicted: " << victim << endl;
        cache.used_memory -= cache.modSizes.find(victim)->second;
        if (cache.used_memory < 0) cache.used_memory = 0;
        cache.numRecompressions++;
    }
	if (debugCacheSim){
		cout << "---Cache Contents---\n";
		for(deque<string>::iterator it = cache.cacheContents.begin(); it != cache.cacheContents.end(); it++)
			cout << "\t" << (*it) << endl;
	}
}

void evict_Optimal(CryoCache& cache){
    if (cache.victimList.size() > 0){
        string victimInstruction = cache.victimList[0];    
        int victimSize = cache.modSizes.find(victimInstruction)->second;
        bool performedEviction = false;
        for(deque<string>::iterator it = cache.cacheContents.begin(); it != cache.cacheContents.end(); ){
            if ((*it) == victimInstruction) {
                cache.cacheContents.erase(it);
                performedEviction = true;
            }
            else ++it;
        }
        for(vector<string>::iterator it = cache.victimList.begin(); it != cache.victimList.end();){
            if ((*it) == victimInstruction && performedEviction){
                cache.victimList.erase(it);
            }
            else ++it;
        }
        if (performedEviction){
            if(debugCacheSim) cout << "Evicted: " << victimInstruction << endl;
            cache.used_memory -= victimSize;
            if (cache.used_memory < 0) cache.used_memory = 0;
            cache.numRecompressions++;
        }
    }
}

bool fillCache(CryoCache& cache, int instSize, int decompressionSize, string curInst){
    if(debugCacheSim){
        cout << "Current Free Memory: " << cache.capacity - cache.used_memory << endl;
        cout << "Filling With Instruction: " << curInst << " of size: " << instSize << " decomp size:" << decompressionSize << endl;
    }

	if (instSize > cache.capacity){
		if(debugCacheSim) cout << "Slicing module" << endl;
		int moduleSlices = ceil(instSize / cache.capacity);
		int i;	
		for (i=0;i<moduleSlices;i++){
			while (!fillCache(cache,cache.capacity,decompressionSize,curInst)) evict(cache); 
		}
		return true;
	}

	// Case 1: Successful Fill
    if (instSize + cache.used_memory/* + decompressionSize*/ <= cache.capacity){
        cache.used_memory += instSize;
        cache.cacheContents.push_back(curInst);
        cache.numDecompressions++;
		cache.decompressionMap[curInst]++;

        if(debugCacheSim){
            cout << "Success" << endl;
            cout << "New Free Memory: " << cache.capacity - cache.used_memory;
//            cout << "New Cache: " << endl;
//            for(deque<string>::iterator it = cache.cacheContents.begin(); it!= cache.cacheContents.end();++it)
//                cout << (*it) << endl;
        }
        return true;
    }
    return false;
}
bool fillCache_Optimal(CryoCache& cache, int instSize, int decompressionSize, string curInst){
    if(debugCacheSim){
        cout << "Current Free Memory: " << cache.capacity - cache.used_memory << endl;
        cout << "Filling With Instruction: " << curInst << " of size: " << instSize << " decomp size:" << decompressionSize << endl;
    }

	if (instSize > cache.capacity){
		if(debugCacheSim) cout << "Slicing module" << endl;
		int moduleSlices = ceil(instSize / cache.capacity);
		int i;	
		for (i=0;i<moduleSlices;i++){
			while (!fillCache(cache,cache.capacity,decompressionSize,curInst)) evict(cache); 
		}
		return true;
	}

	// Case 1: Successful Fill
    if (instSize + cache.used_memory/* + decompressionSize*/ <= cache.capacity){
        cache.used_memory += instSize;
        cache.cacheContents.push_back(curInst);
        cache.numDecompressions++;
		cache.decompressionMap[curInst]++;
        cache.callFrequency[curInst] -= 1;
        if(debugCacheSim) cout << "Calls Left: " << curInst << ":" << cache.callFrequency[curInst] << endl;
        if (cache.callFrequency[curInst] == 0) {
            if(debugCacheSim) cout << "Adding to victims2: " << curInst << endl;
            cache.victimList.push_back(curInst);
        }

        if(debugCacheSim){
            cout << "Success" << endl;
            cout << "New Free Memory: " << cache.capacity - cache.used_memory;
        }
        return true;
    }
    else if (cache.victimList.size() > 0){
        if(debugCacheSim) cout << "Can Evict" << endl;
        evict_Optimal(cache); 
        return fillCache_Optimal(cache, instSize, decompressionSize, curInst);
    }
    else {
        cache.capacity = cache.used_memory + instSize;
        if(debugCacheSim) cout << "New Cache Capacity: " << cache.capacity << endl;
        cache.used_memory = cache.capacity;
        cache.cacheContents.push_back(curInst);
        cache.numDecompressions++;
        cache.decompressionMap[curInst]++;
        cache.callFrequency[curInst] -= 1;
        if (cache.callFrequency[curInst] <= 0) {
            if(debugCacheSim) cout << "Adding to victims3: " << curInst << endl;
            cache.victimList.push_back(curInst);
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
            while( !fillCache(cache, instructionSize, decompressionSize, currentInstruction) ) evict(cache);
            cache.numMisses++;
        }
        else {
            cache.numHits++;
            if (debugCacheSim) cout << "Cache Hit: " << currentInstruction << endl;
        }
    }
}

void runCache_Optimal(CryoCache& cache){
//    for(vector<string>::iterator inst = cache.vectCalls.begin(); inst != cache.vectCalls.end(); ++inst){
    for(int i = 0; i < cache.vectCalls.size(); ++i){
        string currentInstruction = cache.vectCalls[i];
        int instructionSize = cache.modSizes.find(currentInstruction)->second;
		int decompressionSize = cache.decompressionRequirementsMap.find(currentInstruction)->second;
        if ( find(cache.cacheContents.begin(), cache.cacheContents.end(), currentInstruction) == cache.cacheContents.end() ) {
            // Cache Miss
            while( !fillCache(cache, instructionSize, decompressionSize, currentInstruction) ) evict_NextUse(cache, (i + 1));
            cache.numMisses++;
            if(cache.nextUse[currentInstruction].size() > 2)
                cache.nextUse[currentInstruction].pop_front();
            else cache.nextUse[currentInstruction].clear();
            
        }
        else {
            // Cache Hit
            cache.numHits++;
            cache.callFrequency[currentInstruction] -= 1;
            if(cache.nextUse[currentInstruction].size() > 2)
                cache.nextUse[currentInstruction].pop_front();
            else cache.nextUse[currentInstruction].clear();

            if (cache.callFrequency[currentInstruction] <= 0){
                if(debugCacheSim) cout << "Adding to victims1: " << currentInstruction << endl;
                cache.victimList.push_back(currentInstruction);
            }
            if (debugCacheSim) cout << "Cache Hit: " << currentInstruction << endl;
        }
    }
    if (debugCacheSim){
        for(map<string,int>::iterator it = cache.callFrequency.begin(); it != cache.callFrequency.end(); ++it){
//            cout << it-> first << ":" << it->second << endl;
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
        cout << "Number of evictions: " << cache.numEvictions << endl;

		if(debugCacheSim) {
            for(map<string,int>::iterator it = cache.decompressionMap.begin(); it!=cache.decompressionMap.end();++it){
			    cout << it->first << " " << it->second << endl;
            }
		}
    }
    else if(workflowIntegrate == 1){ 
        cout << cache.numDecompressions << endl;
		cout << cache.numEvictions << endl;
		for(map<string,int>::iterator it = cache.decompressionMap.begin(); it!=cache.decompressionMap.end();++it){
    		cout << it->first << ":" << it->second << endl;
		}
		cout << cache.vectCalls.size() << endl;
    }
}

int main( int argc, char *argv[]){
    if (argc < 7){
        cout << "Error: Too Few Parameters Specified" << endl;
        cout << "Usage: " << "[cache capacity] [cache associativity] [eviction policy] [benchmark name] [caching strategy] [workflow printing] " << endl;
        exit(1);
    }
    CryoCache cache;
    int cache_flag = atoi(argv[5]);
    int in_cap = atoi(argv[1]);
    initializeCache(cache, in_cap, argv[2], argv[3]);
    readBenchmark(cache, argv[4], cache_flag);
    if (cache_flag == 1) runCache_Optimal(cache);
    else runCache(cache);
    printStatistics(cache, argv[4], atoi(argv[6]));
    return 0;
}
