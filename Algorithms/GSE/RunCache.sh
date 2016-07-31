#!/bin/bash

g++ CacheSim.cpp -o cachesim &&
./cachesim 317366 "full" "FIFO" "GSE" > cacherun1.txt
./cachesim 310001 "full" "FIFO" "GSE" > cacherun2.txt
./cachesim 310000 "full" "FIFO" "GSE" > cacherun3.txt
./cachesim 309999 "full" "FIFO" "GSE" > cacherun4.txt
./cachesim 309998 "full" "FIFO" "GSE" > cacherun5.txt
./cachesim 309997 "full" "FIFO" "GSE" > cacherun6.txt
cat cacherun1.txt > cacherun.txt
cat cacherun2.txt >> cacherun.txt
cat cacherun3.txt >> cacherun.txt
cat cacherun4.txt >> cacherun.txt
cat cacherun5.txt >> cacherun.txt
cat cacherun6.txt >> cacherun.txt

