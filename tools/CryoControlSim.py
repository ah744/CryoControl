#!/usr/bin/python
import numpy
import scipy
import sys
import subprocess
import os
import time
import resource
import psutil
import operator
import matplotlib.pyplot as plt
import figureplot as fp 
import FullSuite as fs

if(len(sys.argv)<2):
    print "Too few arguments specified..."
    print "Usage: python CryoControlSim.py <benchmark>"
    exit(1)

absScriptsDir = os.path.abspath(os.getcwd()) 
fullPathInput = str(sys.argv[1])
splitInput = fullPathInput.split("/")
algsDirectoryList = splitInput[:-1]
algsDirectory = "/".join(algsDirectoryList)
benchName = splitInput[-1]

if benchName == "full_suite":
    benchData = fs.full_suite()
    maxBenchDomain = 0
    for item in benchData:
    	if len(benchData[item]) > maxBenchDomain:
    		maxBenchDomain = len(benchData[item])
    domain_full = numpy.arange(maxBenchDomain)
    domain_full_proper = []
    for item in reversed(domain_full):
    	domain_full_proper.append(item)
    print domain_full_proper
    print "---------------"
    print benchData
    fs.plot(domain_full_proper,benchData,"full")
    exit(1)

print "------------Cryogenic Control Module Cache Simulator---------------"
compressionAlgorithm = "scz"

print "Running: " + benchName
print "[ccs][0]: Performing Module Extraction"

if(not os.path.exists("Algs")):
	os.makedirs("Algs")
os.chdir("Algs")
newPathInput = "../" + fullPathInput
scriptsDir = "../../"

if(not os.path.exists(benchName)):
    os.makedirs(benchName)

os.chdir(benchName)
newPathInput = "../" + newPathInput

if not os.path.isfile("moduleextractioncomplete"):
    subprocess.call([scriptsDir + 'moduleextraction', newPathInput])
    moduleFilePath = scriptsDir + algsDirectory + "/" + benchName + "modules"
    subprocess.call(['mv', moduleFilePath, "."]) 
    subprocess.call(['touch', "moduleextractioncomplete"])

print "[ccs][0]: Module Extraction Complete"
print "[ccs][1]: Linking Leaf Modules"

if not os.path.isfile("linkercomplete"):
    subprocess.call([scriptsDir + 'linker'])
    subprocess.call(['touch', "linkercomplete"])

print "[ccs][1]: Linking Complete"
print "[ccs][2]: Compressing Modules"

def setlimits():
	resource.setrlimit(resource.RLIMIT_RSS, (1000, 1000))

def compress_decompress(compressionAlgorithm,switch):
	compressionStatistics = {}
	memoryUsageStatistics = {}
	for file in os.listdir(os.getcwd()):
	    if file.endswith(".bin"):
			filename = str(file) 
			if compressionAlgorithm == "zip":
                                t0 = time.clock()
				if switch == "compress":
					p = subprocess.Popen(["zip", "-r", str(filename + ".zip"), str(filename)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				else:
					p = subprocess.Popen(["unzip", "-f", str(filename + ".zip")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				ru = os.wait4(p.pid,0)[2]
                                t1 = time.clock()
				usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
                                cpu_time = t1-t0
				mem_used = usage_end.ru_maxrss
				memoryUsageStatistics[filename] = mem_used
				compressionStatistics[filename] = cpu_time			
			elif compressionAlgorithm == "tar":
                                t0 = time.clock()
				if switch == "compress":
				   	p = subprocess.Popen([compressionAlgorithm, "-zcvf", str(file + ".tar"), file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				else:
				   	p = subprocess.Popen([compressionAlgorithm, "-xvf", str(file + ".tar"), file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			   	ru = os.wait4(p.pid,0)[2]
                                t1 = time.clock()
                                cpu_time = t1-t0
			   	usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
			   	mem_used = usage_end.ru_maxrss
				memoryUsageStatistics[filename] = mem_used
			   	compressionStatistics[filename] = cpu_time			
			elif compressionAlgorithm == "scz":
				usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
                                t0 = time.clock()
				if switch == "compress":
					p = subprocess.Popen([str(compressionAlgorithm + "_compress"), file], stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
				else:
					p = subprocess.Popen([str(compressionAlgorithm + "_decompress"), str(file+".scz")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				ru = os.wait4(p.pid,0)[2]
                                t1 = time.clock()
                                cpu_time = t1-t0
				usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
				mem_used = ru.ru_maxrss 
				memoryUsageStatistics[filename] = mem_used
				compressionStatistics[filename] = cpu_time			
			elif compressionAlgorithm == "gzip":
				usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
                                t0 = time.clock()
				if switch == "compress":
					p = subprocess.Popen([compressionAlgorithm,"-f", "-k", "-S", ".gzip", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
				        ru = os.wait4(p.pid,0)[2]
                                        t1 = time.clock()
				else:
                                        t0 = time.clock()
					p = subprocess.Popen([compressionAlgorithm,"-f", "-d", "-k", str(file+".gzip")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				        ru = os.wait4(p.pid,0)[2]
                                        t1 = time.clock()
                                cpu_time = t1-t0
				usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
				mem_used = ru.ru_maxrss 
				memoryUsageStatistics[filename] = mem_used
				compressionStatistics[filename] = cpu_time			
			elif compressionAlgorithm == "bzip2":
				usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
                                t0 = time.clock()
				if switch == "compress":
					p = subprocess.Popen([compressionAlgorithm, "-k","-s", "-f",file], stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
				else:
					subprocess.call(['cp', str(file+".bz2"), str(file+".bzip2")])
                                        t0 = time.clock()
					p = subprocess.Popen(["bunzip2", "-k","-f","-s", str(file+".bz2")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				ru = os.wait4(p.pid,0)[2]
                                t1 = time.clock()
				usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
                                cpu_time = t1 - t0
				mem_used = ru.ru_maxrss 
				memoryUsageStatistics[filename] = mem_used
				compressionStatistics[filename] = cpu_time			
	return [compressionStatistics,memoryUsageStatistics]

print "Compressing..."
compress_decompress("bzip2","compress")
compress_decompress("scz","compress")
compress_decompress("zip","compress")
compress_decompress("tar","compress")
compress_decompress("gzip","compress")
print "Decompressing..."
compressionStatisticsBZIP2 = compress_decompress("bzip2","decompress")[0]
compressionStatisticsSCZ = compress_decompress("scz","decompress")[0]
compressionStatisticsZIP = compress_decompress("zip","decompress")[0]
compressionStatisticsTAR = compress_decompress("tar","decompress")[0]
compressionStatisticsGZIP = compress_decompress("gzip","decompress")[0]

print "Collecting Statistics..."
memoryUsageStatisticsBZIP2 = compress_decompress("bzip2","decompress")[1]
memoryUsageStatisticsSCZ = compress_decompress("scz","decompress")[1]
memoryUsageStatisticsZIP = compress_decompress("zip","decompress")[1]
memoryUsageStatisticsTAR = compress_decompress("tar","decompress")[1]
memoryUsageStatisticsGZIP = compress_decompress("gzip","decompress")[1]

memoryUsageMax = []
memoryUsageMax.append(numpy.amax(memoryUsageStatisticsBZIP2.values()))
memoryUsageMax.append(numpy.amax(memoryUsageStatisticsSCZ.values()))
memoryUsageMax.append(numpy.amax(memoryUsageStatisticsZIP.values()))
memoryUsageMax.append(numpy.amax(memoryUsageStatisticsTAR.values()))
memoryUsageMax.append(numpy.amax(memoryUsageStatisticsGZIP.values()))

print "[ccs][2]: Module Compression Complete"
print "[ccs][3]: Preparing Simulator Input Files"

#----------- Create Module Sizes File -----------#
benchSizeFileName = benchName + "sizes.txt"
outputFile = open("filesizes.txt", "w")

filesizes_compressed = {}
filesizes_decompressed = {}
sumDecompressedModules = 0
sumDecompressedLeaves = 0
sumCompressedModules = 0
sumCompressedLeaves = 0

for file in os.listdir(os.getcwd()):
	if file.endswith(".bin"):
		sumDecompressedModules += os.path.getsize(file)
		trueFileName = file[0:-4]
		filesizes_decompressed[file] = os.path.getsize(file)
		outputFile.write(trueFileName + " " + str(os.path.getsize(file)) + "\n")
for file in os.listdir(os.getcwd()):
	if file.endswith(compressionAlgorithm):
		sumCompressedModules += os.path.getsize(file)
		sumCompressedLeaves += os.path.getsize(file)
		filesizes_compressed[file] = os.path.getsize(file)
		outputFile.write( file + " " + str(os.path.getsize(file)) + "\n")
outputFile.close()

with open(benchSizeFileName, "w") as sizesFile:
	for filepair in filesizes_decompressed:
		filename = filepair[:-4]
		filesize = filesizes_decompressed[filepair]
		sizesFile.write(filename + " " + str(filesize) + "\n")
sizesFile.close()
callStackFileName = benchName + "calls.txt"
subprocess.call(['mv', 'main.calls.txt', callStackFileName])

with open(str(benchName + 'decomp.sizes.txt'), 'w') as decompSizesFile:
	for item in memoryUsageStatisticsGZIP:
		decompSizesFile.write(item + " " + str(memoryUsageStatisticsGZIP[item]) + "\n")	
decompSizesFile.close()

print "[ccs][3]: Simulator Inputs Prepared"
print "[ccs][4]: Preparing Data Ranges"

numModules = len(filesizes_compressed)
sorted_filesizes_decompressed = sorted(filesizes_decompressed.items(), key=operator.itemgetter(1))
ordered_filesizes_decompressed = []
for pair in reversed(sorted_filesizes_decompressed):
    ordered_filesizes_decompressed.append(pair)
largestModuleSize = ordered_filesizes_decompressed[0][1]

ranges = []
newValue = sumDecompressedModules
moduleRanges = []

for x in range(6,0,-1):
    moduleRanges.append(int((x/6.)*numModules))
for modulecount in moduleRanges:
    newValue = sumDecompressedModules
    for x in range(numModules - modulecount):
        newValue -= sorted_filesizes_decompressed[x][1]
    ranges.append(newValue)

print "Current Ranges:"
print ranges
print "Current Module Ranges:"
print moduleRanges

for x in [8,4,2,1]:
    newValue = largestModuleSize
    print "Trying: " + str(x)
    if x < numModules and x > moduleRanges[-1]:
        print "Fitting into current list"
        for item in moduleRanges:
            if item < x:
                print "Found correct location"
                moduleRanges.insert(moduleRanges.index(item),x)
                break
        if x > 1:
            print "Calculating correct capacity"
            for i in range(x):
                newValue += sorted_filesizes_decompressed[x][1]
        ranges.insert(moduleRanges.index(x),newValue)
        print "Finished adding capacity: " + str(newValue) + " at module count: " + str(x)
    elif x < numModules and x < moduleRanges[-1]:
        print "Adding: " + str(x)
        if x > 1:
            for i in range(x):
                newValue += sorted_filesizes_decompressed[x][1]
        print "New capacity to be added: " + str(newValue)
        if newValue < ranges[-1]:
            ranges.append(newValue)
            moduleRanges.append(x)
            print "Finished adding capacity: " + str(newValue) + " at module count: " + str(x)

for x in ranges:
    if x < largestModuleSize:
        ranges.remove(x)

print "Final Module Ranges:"
print moduleRanges

#   Step sizes of decrementing by a single module, fine grained
#for pair in sorted_filesizes_decompressed:
#    newValue -= pair[1]
#    ranges.append(newValue) 
#for x in ranges:
#    if x < largestModuleSize:
#        ranges.remove(x)


print "[ccs][4]: Data Ranges Prepared"
print "[ccs][5]: Performing Simulation"

compData = {}
cpuDataBZIP2 = [] 
cpuDataSCZ = [] 
cpuDataZIP = [] 
cpuDataTAR = [] 
cpuDataGZIP = [] 
total_cpu_usage_bzip2 = 0
total_cpu_usage_scz = 0
total_cpu_usage_zip = 0
total_cpu_usage_tar = 0
total_cpu_usage_gzip = 0

memDataBZIP2 = [] 
memDataSCZ = [] 
memDataZIP = [] 
memDataTAR = [] 
memDataGZIP = [] 
total_mem_usage_bzip2 = 0
total_mem_usage_scz = 0
total_mem_usage_zip = 0
total_mem_usage_tar = 0
total_mem_usage_gzip = 0

for capacity in ranges:
	print "\tSimulating Capacity: " + str(capacity)
	output =  subprocess.check_output([scriptsDir + 'cachesim', str(capacity), 'full', 'FIFO', benchName, '1'])
	outputSplit = output.split("\n")
	compData[capacity] = outputSplit[0] 
	outputSplit = outputSplit[1:-1]
	for item in outputSplit:
		itemSplit = item.split(":")
		moduleName = itemSplit[0] + ".bin"
		numberOfDecompressions = int(itemSplit[1])
		compressionUsageBZIP2 = compressionStatisticsBZIP2[moduleName]
		compressionUsageSCZ = compressionStatisticsSCZ[moduleName]
		compressionUsageZIP = compressionStatisticsZIP[moduleName]
		compressionUsageTAR = compressionStatisticsTAR[moduleName]
		compressionUsageGZIP = compressionStatisticsGZIP[moduleName]
		total_cpu_usage_bzip2 += (numberOfDecompressions * compressionUsageBZIP2)
		total_cpu_usage_scz += (numberOfDecompressions * compressionUsageSCZ)
		total_cpu_usage_zip += (numberOfDecompressions * compressionUsageZIP)
		total_cpu_usage_tar += (numberOfDecompressions * compressionUsageTAR)
		total_cpu_usage_gzip += (numberOfDecompressions * compressionUsageGZIP)

		memoryUsageBZIP2 = memoryUsageStatisticsBZIP2[moduleName]
		memoryUsageSCZ = memoryUsageStatisticsSCZ[moduleName]
		memoryUsageZIP = memoryUsageStatisticsZIP[moduleName]
		memoryUsageTAR = memoryUsageStatisticsTAR[moduleName]
		memoryUsageGZIP = memoryUsageStatisticsGZIP[moduleName]
		total_mem_usage_bzip2 += (numberOfDecompressions * memoryUsageBZIP2)
		total_mem_usage_scz += (numberOfDecompressions * memoryUsageSCZ)
		total_mem_usage_zip += (numberOfDecompressions * memoryUsageZIP)
		total_mem_usage_tar += (numberOfDecompressions * memoryUsageTAR)
		total_mem_usage_gzip += (numberOfDecompressions * memoryUsageGZIP)

	cpuDataBZIP2.append(total_cpu_usage_bzip2)
	cpuDataSCZ.append(total_cpu_usage_scz)
	cpuDataZIP.append(total_cpu_usage_zip)
	cpuDataTAR.append(total_cpu_usage_tar)
	cpuDataGZIP.append(total_cpu_usage_gzip)
	total_cpu_usage_bzip2 = 0
	total_cpu_usage_scz = 0
	total_cpu_usage_zip = 0
	total_cpu_usage_tar = 0
	total_cpu_usage_gzip = 0

	memDataBZIP2.append(total_mem_usage_bzip2)
	memDataSCZ.append(total_mem_usage_scz)
	memDataZIP.append(total_mem_usage_zip)
	memDataTAR.append(total_mem_usage_tar)
	memDataGZIP.append(total_mem_usage_gzip)
	total_mem_usage_bzip2 = 0
	total_mem_usage_scz = 0
	total_mem_usage_zip = 0
	total_mem_usage_tar = 0
	total_mem_usage_gzip = 0



print "[ccs][5]: Simulation Complete"
print "[ccs][6]: Beginning Data Analysis"

compData = sorted(compData.items(),key=operator.itemgetter(0))
cpuData = []
cpuData.append(cpuDataBZIP2)
cpuData.append(cpuDataSCZ)
cpuData.append(cpuDataZIP)
cpuData.append(cpuDataTAR)
cpuData.append(cpuDataGZIP)

memData = []
memData.append(memDataBZIP2)
memData.append(memDataSCZ)
memData.append(memDataZIP)
memData.append(memDataTAR)
memData.append(memDataGZIP)


fp.figplot(benchName,numModules,compData,cpuData,moduleRanges,"cputs")
fp.figplot(benchName,numModules,compData,cpuData,moduleRanges,"cpu")
fp.figplot(benchName,numModules,memoryUsageMax,cpuData,moduleRanges,"max")

with open (str(benchName + "cputs"), 'w') as f:
	for item in cpuData:
		for val in item:
			f.write(str(int(numpy.ceil(val*(2.8*10**9)))) + " ")
		f.write("\n")
f.close()

print "[ccs][6] Data Analysis Complete" 
print "[ccs][7] Full Suite Analysis" 


