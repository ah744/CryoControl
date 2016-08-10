#!/usr/bin/python
import numpy
import scipy
import sys
import subprocess
import os

def process_call_stack(benchName):
    callFileName = benchName + "calls.txt"
    callFile = open(callFileName, "w")




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
#compressionAlgorithm = input("Specify Compression Algorithm: ")
compressionAlgorithm = "scz"

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
print "ccs[2]: Compressing Modules"

for file in os.listdir(os.getcwd()):
    if file.endswith(".bin"):
        if compressionAlgorithm == "zip":
            subprocess.call([compressionAlgorithm, " -r", str(file + ".zip"), file])
        elif compressionAlgorithm == "tar":
            subprocess.call([compressionAlgorithm, "-zcvf", str(file + ".gz"), file])
        elif compressionAlgorithm == "scz":
            subprocess.call([str(compressionAlgorithm + "_compress"), file])

print "ccs[2]: Module Compression Complete"
print "ccs[3]: Preparing Simulator Input Files"

#----------- Create Module Sizes File -----------#
benchSizeFileName = benchName + "sizes.txt"
outputFile = open("filesizes.txt", "w")

for file in os.listdir(os.getcwd()):
    if file.endswith(".bin"):
        trueFileName = file[0:-4]
        outputFile.write(trueFileName + " " + str(os.path.getsize(file)) + "\n")
for file in os.listdir(os.getcwd()):
    if file.endswith(compressionAlgorithm):
        outputFile.write( file + " " + str(os.path.getsize(file)) + "\n")

outputFile.close()
sizesFile = open(benchSizeFileName, "w")

for file in os.listdir(os.getcwd()):
    if file.endswith(".bin"):
        trueFileName = file[0:-4]
        sizesFile.write(trueFileName + " " + str(os.path.getsize(file)) + "\n")

sizesFile.close()

callStackFileName = benchName + "calls.txt"
subprocess.call(['mv', 'main.calls.txt', callStackFileName])

print "ccs[3]: Simulator Inputs Prepared"
print "ccs[4]: Performing Simulation"

subprocess.call(['../cachesim', str(1000000), 'full', 'FIFO', benchName]) 

print "ccs[4]: Simulation Complete"

