#!/bin/bash

g++ Linker.cpp -o linker &&
./linker "ORACLE_IP0" > linker.out
