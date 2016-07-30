#!/bin/bash

g++ Linker.cpp -o linker &&
./linker $1 > linker.out
