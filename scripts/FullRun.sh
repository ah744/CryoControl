#!/bin/bash
benchmark=$1
./RunModuleExtraction.sh $1
./ExtractLoop.sh $1.modules
