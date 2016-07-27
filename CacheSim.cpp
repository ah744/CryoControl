#include <iostream>
#include <string>

using namespace std;

struct CryoCache {
    int capacity;
    const char* associativity;
    const char* eviction;
    int used_memory;
    CryoCache():capacity(1024),associativity("full"),eviction("LRU"),used_memory(0) { }
}; 

void initializeCache(CryoCache cache, int input_cap, char* input_associativity, char* input_eviction){
    cache.capacity = input_cap;
    cache.associativity = input_associativity;
    cache.eviction = input_eviction;
}

void readBenchmark(){
    //TODO: Read in an unrolled call stack of a benchmark
    //      Read in module names and uncompressed sizes
    //      Perform cache analysis
    //      Keep track of statistics
}

void printStatistics(){
    //TODO: Print out the:
    //      1. Number of decompressions performed
    //      2. Number of recompressions performed
}

int main( int argc, char* argv[]){
    if (argc < 3){
        cerr << "Usage: " << "[cache capacity] [cache associativity] [eviction policy]" << endl;
    }
    CryoCache cache;
    int in_cap = atoi(argv[1]);
    initializeCache(cache, in_cap, argv[2], argv[3]);
    readBenchmark();
    printStatistics();
    cout << "Complete" << endl;
    return 0;
}
