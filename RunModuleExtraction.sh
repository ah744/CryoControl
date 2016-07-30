#!/bin/bash
key="$1"
g++ ModuleExtraction.cpp -o moduleextraction &&
./moduleextraction $key
