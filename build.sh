#!/bin/bash

g++ CacheSim.cpp -o cachesim &&
./cachesim 2300000 "full" "FIFO" "BWT" > cacherun1.txt
./cachesim 4600000 "full" "FIFO" "BWT" > cacherun2.txt
./cachesim 6900000 "full" "FIFO" "BWT" > cacherun3.txt
./cachesim 9200000 "full" "FIFO" "BWT" > cacherun4.txt
./cachesim 11500000 "full" "FIFO" "BWT" > cacherun5.txt
./cachesim 13800000 "full" "FIFO" "BWT" > cacherun6.txt
./cachesim 16100000 "full" "FIFO" "BWT" > cacherun7.txt
cat cacherun1.txt > cacherun.txt
cat cacherun2.txt >> cacherun.txt
cat cacherun3.txt >> cacherun.txt
cat cacherun4.txt >> cacherun.txt
cat cacherun5.txt >> cacherun.txt
cat cacherun6.txt >> cacherun.txt
cat cacherun7.txt >> cacherun.txt

