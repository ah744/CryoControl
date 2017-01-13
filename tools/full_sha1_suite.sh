#!/bin/bash
./CryoControlSim.py ../Algorithms/SHA1/SIMD_1/0k/sha1.n1024.flat000k. &&      
./CryoControlSim.py ../Algorithms/SHA1/SIMD_1/1k/sha1.n1024.flat001k. && 
./CryoControlSim.py ../Algorithms/SHA1/SIMD_1/10k/sha1.n1024.flat010k. && 
./CryoControlSim.py ../Algorithms/SHA1/SIMD_1/100k/sha1.n1024.flat100k. &&
./CryoControlSim.py ../Algorithms/SHA1/SIMD_1/2M/sha1.n1024.flat2M. &&
./CryoControlSim.py ../Algorithms/SHA1/SIMD_1/25M/sha1.n1024.flat25M.
