#!/usr/bin/python
import numpy
import scipy
import sys
import subprocess
import os

if(len(sys.argv)<2):
    print "Too few arguments specified..."
    print "Usage: python CryoControlSim.py <benchmark>"
    exit(1)

fullPathInput = str(sys.argv[1])
splitInput = fullPathInput.split("/")
algsDirectoryList = splitInput[:-1]
algsDirectory = "/".join(algsDirectoryList)
benchName = splitInput[-1]

print "------------Cryogenic Control Module Cache Simulator---------------"
print "Running: " + benchName
print "ccs[0]: Performing Module Extraction"

if(not os.path.exists(benchName)):
    os.makedirs(benchName)

os.chdir(benchName)
newPathInput = "../" + fullPathInput

subprocess.call(['../moduleextraction', newPathInput])
moduleFilePath = "../" + algsDirectory + "/" + benchName + "modules"
subprocess.call(['mv', moduleFilePath, "."]) 

print "ccs[0]: Module Extraction Complete"
print "ccs[1]: Linking Leaf Modules"

subprocess.call(['../linker'])

print "ccs[1]: Linking Complete"
print "ccs[2]: Performing Simulation"

print "ccs[3]: Simulation Complete"

