#!/bin/bash

g++ Linker.cpp -o linker &&
./linker "ORACLE_IP0" > linker.out
./linker "ORACLE_IP1" > linker.out
./linker "ORACLE_IP2" > linker.out
./linker "ORACLE_IP3" > linker.out
./linker "TIMESTEP" > linker.out
