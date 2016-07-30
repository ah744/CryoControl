#!/bin/bash
benchmark=$1
./RunModuleExtraction.sh $1
./LinkerLoop.sh $1.modules 
