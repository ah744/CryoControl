#!/usr/bin/python
import numpy
import scipy
import sys
import subprocess
import os
import operator
import matplotlib.pyplot as plt


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

filesizes_compressed = {}
filesizes_decompressed = {}
sumDecompressedModules = 0
sumCompressedModules = 0

for file in os.listdir(os.getcwd()):
    if file.endswith(".bin"):
        sumDecompressedModules += os.path.getsize(file)
        trueFileName = file[0:-4]
        filesizes_decompressed[file] = os.path.getsize(file)
        outputFile.write(trueFileName + " " + str(os.path.getsize(file)) + "\n")
for file in os.listdir(os.getcwd()):
    if file.endswith(compressionAlgorithm):
        sumCompressedModules += os.path.getsize(file)
        filesizes_compressed[file] = os.path.getsize(file)
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
print "ccs[4]: Preparing Data Ranges\n"

numModules = len(filesizes_compressed)
print "Total Number of Modules: " + str(numModules) 
print "Sizes of Modules" + str(len(filesizes_compressed)) 
sorted_filesizes_decompressed = sorted(filesizes_decompressed.items(), key=operator.itemgetter(1))
ordered_filesizes_decompressed = []
for pair in reversed(sorted_filesizes_decompressed):
    ordered_filesizes_decompressed.append(pair)
    print str(pair[1]) + "  " + pair[0] 
print "Total Decompressed Module Size: " + str(sumDecompressedModules) + " Bytes"
print "Total Compressed Module Size: " + str(sumCompressedModules) + " Bytes"
largestModuleSize = ordered_filesizes_decompressed[0][1]
print "Largest Module Size: " + str(largestModuleSize) + "\n"

ranges = []
newValue = sumDecompressedModules
ranges.append(newValue)
for pair in sorted_filesizes_decompressed:
    print pair[0]
    newValue -= pair[1]
    ranges.append(newValue) 
for x in ranges:
    if x < largestModuleSize:
        ranges.remove(x)
print ranges


print "ccs[4]: Data Ranges Prepared"
print "ccs[5]: Performing Simulation"

data = {}
for capacity in ranges:
    print "Simulating Capacity: " + str(capacity)
    data[capacity] = int(subprocess.check_output(['../cachesim', str(capacity), 'full', 'FIFO', benchName, 'True']))

print "ccs[5]: Simulation Complete"

data = sorted(data.items(),key=operator.itemgetter(0))

N = len(data)
width = 0.35                      
domain = []
ind = numpy.arange(N)
for x in range(N):
    domain.append(numModules-x)
capacities = []
decompressions = []
for item in reversed(data):
    capacities.append(item[0])
    decompressions.append(item[1])
print capacities
print decompressions
print domain

fig = plt.figure()
ax = fig.add_subplot(111)

rects1 = ax.bar(ind, capacities, width,
                color='black')

ax.set_xlim(-width,len(ind)+width)
ax2 = ax.twinx()
rects2 = ax2.bar(ind+width, decompressions, width,
                    color='blue')
ax2.set_xlim(-width,len(ind)+width)
ax.set_ylabel("Capacity (Bytes)")
ax2.set_ylabel("Decompressions")
ax.set_xlabel("Number of Modules Containable by Cache")
ax.set_title("Cache Capacities and Decompressions Performed")
xTickMarks = domain
ax.set_xticks(ind+width)
xtickNames = ax.set_xticklabels(xTickMarks)
plt.setp(xtickNames, fontsize=10)

## add a legend
ax.legend( (rects1[0], rects2[0]), ('Cache Capacity', 'Decompressions') )

plt.show()


































