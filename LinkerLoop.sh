#!/bin/bash
while IFS='' read -r line || [[ -n $line ]]; do
    echo "Compiling Linker"
    g++ Linker.cpp -o linker &&
    echo "Linking Module: $line"
    ./linker $line >> linker.out
done < "$1"
