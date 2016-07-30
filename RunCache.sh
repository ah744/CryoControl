#!/bin/bash

g++ CacheSim.cpp -o cachesim &&
./cachesim 8808 "full" "FIFO" "SQRT" > cacherun1.txt
./cachesim 6606 "full" "FIFO" "SQRT" > cacherun2.txt
./cachesim 4404 "full" "FIFO" "SQRT" > cacherun3.txt
./cachesim 3303 "full" "FIFO" "SQRT" > cacherun4.txt
./cachesim 2202 "full" "FIFO" "SQRT" > cacherun5.txt
cat cacherun1.txt > cacherun.txt
cat cacherun2.txt >> cacherun.txt
cat cacherun3.txt >> cacherun.txt
cat cacherun4.txt >> cacherun.txt
cat cacherun5.txt >> cacherun.txt

