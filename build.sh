#!/bin/bash

g++ CacheSim.cpp -o CacheSim &&
./CacheSim 1024 "full" "LRU"
