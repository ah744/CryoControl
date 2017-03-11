#!/usr/bin/python
import numpy
import sys
import subprocess
import os
import time
import resource
import psutil
import operator
import csv
import xlsxwriter as xl
import matplotlib.pyplot as plt
import FigurePlot as fp 
import FigPlot as fplot 
import HistogramPlot as hp 
import FullSuite as fs

if(len(sys.argv)<2):
    print "Too few arguments specified..."
    print "Usage: python CryoControlSim.py <benchmark> <capacity>"
    exit(1)

absScriptsDir = os.path.abspath(os.getcwd()) 
baseDir = "/Users/Adam/Research/CryoControl/"

fullPathInput = str(sys.argv[1])
fullPathInputSplit = fullPathInput.split('/')
algInputFile = baseDir + '/'.join(fullPathInputSplit[1:]) + 'lpfs'
inliningInfoFile = baseDir + '/'.join(fullPathInputSplit[1:-1]) + '/inlined.out'
cacheCap = 0
if len(sys.argv) == 3:
    cacheCap = int(sys.argv[2])
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
compressionAlgorithm = "gzip"

print "Running: " + benchName
print "[ccs][0]: Performing Module Extraction"

if(not os.path.exists("Algs")):
	os.makedirs("Algs")
os.chdir("Algs")
newPathInput = "../" + fullPathInput
scriptsDir = "../../"
binDir = "bin/"

if(not os.path.exists(benchName)):
    os.makedirs(benchName)

os.chdir(benchName)
newPathInput = "../" + newPathInput

if not os.path.isfile("moduleextractioncomplete"):
    subprocess.call([scriptsDir + binDir + 'moduleextraction', newPathInput])
    moduleFilePath = scriptsDir + algsDirectory + "/" + benchName + "modules"
    subprocess.call(['mv', moduleFilePath, "."]) 
    subprocess.call(['touch', "moduleextractioncomplete"])

print "[ccs][0]: Module Extraction Complete"
print "[ccs][1]: Linking Leaf Modules"

if not os.path.isfile("linkercomplete"):
    f = open("errs.out", "wb")
    subprocess.call([scriptsDir + binDir + 'linker'], stdout=f)
    f.close()
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
#
if not os.path.isfile("compressioncomplete"):
	print "Compressing..."
	#compress_decompress("bzip2","compress")
	#compress_decompress("scz","compress")
	#compress_decompress("zip","compress")
	#compress_decompress("tar","compress")
	#compress_decompress("gzip","compress")
	print "Decompressing..."
	#compressionStatisticsBZIP2 = compress_decompress("bzip2","decompress")[0]
	#compressionStatisticsSCZ = compress_decompress("scz","decompress")[0]
	#compressionStatisticsZIP = compress_decompress("zip","decompress")[0]
	#compressionStatisticsTAR = compress_decompress("tar","decompress")[0]
	#compressionStatisticsGZIP = compress_decompress("gzip","decompress")[0]
	#
	print "Collecting Statistics..."
	#memoryUsageStatisticsBZIP2 = compress_decompress("bzip2","decompress")[1]
	#memoryUsageStatisticsSCZ = compress_decompress("scz","decompress")[1]
	#memoryUsageStatisticsZIP = compress_decompress("zip","decompress")[1]
	#memoryUsageStatisticsTAR = compress_decompress("tar","decompress")[1]
	#memoryUsageStatisticsGZIP = compress_decompress("gzip","decompress")[1]
	#
	#memoryUsageMax = []
	#memoryUsageMax.append(numpy.amax(memoryUsageStatisticsBZIP2.values()))
	#memoryUsageMax.append(numpy.amax(memoryUsageStatisticsSCZ.values()))
	#memoryUsageMax.append(numpy.amax(memoryUsageStatisticsZIP.values()))
	#memoryUsageMax.append(numpy.amax(memoryUsageStatisticsTAR.values()))
	#memoryUsageMax.append(numpy.amax(memoryUsageStatisticsGZIP.values()))
	#
	subprocess.call(['touch', "compressioncomplete"])
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
	if file[0].isdigit() and file.endswith(".bin"):
		sumDecompressedModules += os.path.getsize(file)
		trueFileName = file[0:-4]
		filesizes_decompressed[file] = os.path.getsize(file)
		outputFile.write(trueFileName + " " + str(os.path.getsize(file)) + "\n")
for file in os.listdir(os.getcwd()):
	if file[0].isdigit() and file.endswith(compressionAlgorithm):
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

#with open(str(benchName + 'decomp.sizes.txt'), 'w') as decompSizesFile:
#	for item in memoryUsageStatisticsGZIP:
#			decompSizesFile.write(item[:-4] + " " + str(memoryUsageStatisticsGZIP[item]) + "\n")	
#decompSizesFile.close()

print "[ccs][3]: Simulator Inputs Prepared"
print "[ccs][4]: Preparing Data Ranges"

numModules = len(filesizes_compressed)
sorted_filesizes_decompressed = sorted(filesizes_decompressed.items(), key=operator.itemgetter(1))
ordered_filesizes_decompressed = []
for pair in reversed(sorted_filesizes_decompressed):
    ordered_filesizes_decompressed.append(pair)
#largestModuleSize = ordered_filesizes_decompressed[0][1]
#secondLargestModuleSize = largestModuleSize 
#smallestModuleSize = largestModuleSize
#if len(ordered_filesizes_decompressed) > 1:
#    secondLargestModuleSize = ordered_filesizes_decompressed[1][1]
#    smallestModuleSize = sorted_filesizes_decompressed[0][1]

#hp.figplot(benchName, ordered_filesizes_decompressed)

ranges = []
#ranges.append(64)
#ranges.append(128)
#ranges.append(256)
#ranges.append(512)
ranges.append(1024)
ranges.append(2048)
#ranges.append(3000000)
#ranges.append(sumDecompressedModules)
#ranges.append(largestModuleSize)
#if cacheCap == 0 and len(ordered_filesizes_decompressed) > 1:
#	ranges.append(smallestModuleSize)
#	for x in range(4):
#		ranges.append(smallestModuleSize + ordered_filesizes_decompressed[1 - x][1])
#else:
#    ranges.append(cacheCap)
#print ordered_filesizes_decompressed

#   Step sizes of decrementing by a single module, fine grained
#for pair in sorted_filesizes_decompressed:
#    newValue -= pair[1]
#    ranges.append(newValue) 
#for x in ranges:
#    if x < largestModuleSize:
#        ranges.remove(x)


print "[ccs][4]: Data Ranges Prepared"
#
#print "[ccs][5.0]: Gathering Caching Strategy Information"
#callFrequency = {}
#with open (benchName+"calls.txt", 'r') as f:
#    for line in f:
#        if line[:-1] in callFrequency:
#            callFrequency[line[:-1]] += 1    
#        else:
#            callFrequency[line[:-1]] = 1
#    f.close()
#print callFrequency
#
#with open ("call_frequency.txt", 'w') as f:
#    for key, value in callFrequency.iteritems():
#        f.write(key + " " + str(value) + "\n")
#    f.close()
#
print "[ccs][5]: Performing Simulation"

compData = {}
evictData = {}
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

ranges = sorted(ranges, key=float, reverse=True)

print "Current Ranges:"
print ranges

numDistinctModules = len(ordered_filesizes_decompressed)
totalModules = 0

#for capacity in ranges:
#	print "\tSimulating Capacity: " + str(capacity)
#	output =  subprocess.check_output([scriptsDir + binDir + 'cachesim', str(capacity), 'full', 'FIFO', benchName, '1', '1'])
#	outputSplit = output.split("\n")
#	compData[capacity] = outputSplit[0] 
#	evictData[capacity] = outputSplit[1]
#	totalModules = outputSplit[-2]
#	print outputSplit[0]
#	print totalModules
#	outputSplit = outputSplit[2:-2]
#	for item in outputSplit[:-1]:
#		itemSplit = item.split(":")
#		moduleName = itemSplit[0] + ".bin"
#		numberOfDecompressions = int(itemSplit[1])

		#compressionUsageBZIP2 = compressionStatisticsBZIP2[moduleName]
		#compressionUsageSCZ = compressionStatisticsSCZ[moduleName]
		#compressionUsageZIP = compressionStatisticsZIP[moduleName]
		#compressionUsageTAR = compressionStatisticsTAR[moduleName]
		#compressionUsageGZIP = compressionStatisticsGZIP[moduleName]

		#total_cpu_usage_bzip2 += (numberOfDecompressions * compressionUsageBZIP2)
		#total_cpu_usage_scz += (numberOfDecompressions * compressionUsageSCZ)
		#total_cpu_usage_zip += (numberOfDecompressions * compressionUsageZIP)
		#total_cpu_usage_tar += (numberOfDecompressions * compressionUsageTAR)
		#total_cpu_usage_gzip += (numberOfDecompressions * compressionUsageGZIP)

		#memoryUsageBZIP2 = memoryUsageStatisticsBZIP2[moduleName]
		#memoryUsageSCZ = memoryUsageStatisticsSCZ[moduleName]
		#memoryUsageZIP = memoryUsageStatisticsZIP[moduleName]
		#memoryUsageTAR = memoryUsageStatisticsTAR[moduleName]
		#memoryUsageGZIP = memoryUsageStatisticsGZIP[moduleName]

		#total_mem_usage_bzip2 += (numberOfDecompressions * memoryUsageBZIP2)
		#total_mem_usage_scz += (numberOfDecompressions * memoryUsageSCZ)
		#total_mem_usage_zip += (numberOfDecompressions * memoryUsageZIP)
		#total_mem_usage_tar += (numberOfDecompressions * memoryUsageTAR)
		#total_mem_usage_gzip += (numberOfDecompressions * memoryUsageGZIP)

	#cpuDataBZIP2.append(total_cpu_usage_bzip2)
	#cpuDataSCZ.append(total_cpu_usage_scz)
	#cpuDataZIP.append(total_cpu_usage_zip)
	#cpuDataTAR.append(total_cpu_usage_tar)
	#cpuDataGZIP.append(total_cpu_usage_gzip)

	#total_cpu_usage_bzip2 = 0
	#total_cpu_usage_scz = 0
	#total_cpu_usage_zip = 0
	#total_cpu_usage_tar = 0
	#total_cpu_usage_gzip = 0

	#memDataBZIP2.append(total_mem_usage_bzip2)
	#memDataSCZ.append(total_mem_usage_scz)
	#memDataZIP.append(total_mem_usage_zip)
	#memDataTAR.append(total_mem_usage_tar)
	#memDataGZIP.append(total_mem_usage_gzip)

	#total_mem_usage_bzip2 = 0
	#total_mem_usage_scz = 0
	#total_mem_usage_zip = 0
	#total_mem_usage_tar = 0
	#total_mem_usage_gzip = 0

print "[ccs][5]: Simulation Complete"
print "[ccs][6]: Beginning Data Analysis"

# This is for cache  simulation here
#compData = sorted(compData.items(),key=operator.itemgetter(0))
#evictData = sorted(evictData.items(),key=operator.itemgetter(0))
#cpuData = []

#cpuData.append(cpuDataBZIP2)
#cpuData.append(cpuDataSCZ)
#cpuData.append(cpuDataZIP)
#cpuData.append(cpuDataTAR)
#cpuData.append(cpuDataGZIP)
#print compData

memData = []
#memData.append(memDataBZIP2)
#memData.append(memDataSCZ)
#memData.append(memDataZIP)
#memData.append(memDataTAR)
#memData.append(memDataGZIP)

runtime = 0
inlinedLines = 0

with open((benchName + "results"), "w") as out, open((algInputFile), "r") as f:#, open(inliningInfoFile, "r") as inlineInfo:
    for line in f:
        if line.startswith("#Num of SIMD time steps for function main : "):
            lineSplit = line.split(" ")
            runtime = int(lineSplit[-1][:-1])
#	for line in inlineInfo:
#		if line.startswith("Inlined"):
#			lineSplit = line.split(" ")
#			inlinedLines = int(lineSplit[-1])
print "Runtime: " + str(runtime)
#print "Inlined Lines: " + str(inlinedLines)
print "Code Size: " + str(sumDecompressedModules)
print 'Modules Run ' + str(totalModules)
print 'Distinct Modules ' + str(numDistinctModules)
print "[ccs][7]: Writing to csv"

with open("../algs_results.csv", "ab") as output:
	out = csv.writer(output, dialect='excel')
	out.writerow((benchName , '')) 
	#out.writerow(('Decompressions:',''))
	#for pair in compData:
	#	out.writerow((str(pair[0]),pair[1])) 
	#out.writerow(('Evictions',''))
	#for pair in evictData:
	#	out.writerow((str(pair[0]),pair[1])) 
	out.writerow(('Runtime', str(runtime)))
	out.writerow(('Code Size', str(sumDecompressedModules)))
	out.writerow(('Inlined Lines', str(inlinedLines)))
	out.writerow(('Modules Run', str(totalModules)))
	out.writerow(('Distinct Modules', str(numDistinctModules)))


#print "[ccs][7]: Writing to workbook"
#
#
#workbook = xl.Workbook((benchName + "xlsx")) 
#worksheet = workbook.add_worksheet()
#row = 0
#col = 0
#for pair in compData:
#    worksheet.write(row,col,pair[0])
#    worksheet.write(row,col+1,int(pair[1]))
#    row += 1
#worksheet.write(row,col,"Runtime")
#worksheet.write(row,col+1,int(runtime))
#worksheet.write(row+1,col,"Total Modules")
#worksheet.write(row+1,col+1,int(totalModules))
#chart = workbook.add_chart({'type': 'column'})
#chart.add_series({'values':'=Sheet1!$B$1:$B$6'})
#chart.set_x_axis({'values':'=Sheet1!A$1:$A$6'})
#worksheet.insert_chart('A7', chart)
#
#workbook.close()




#print "[ccs][6.1]: Applying Hardware Power Conversion"
#print "[ccs][6.2]: Applying Temperature Level Power Overhead"
#
## Conversion Factors
#RSFQ_factor = 1*10**(-19)
#cryoCMOS_factor = 1*10**(-15)
#
## T Level Parameters
#Penalty_4K = 200
#Penalty_20mK = 50000
#
## Architectural Parameters
#CMOS_ops_per_tick = 21.5*10**6
#RSFQ_ops_per_tick = 21.5*10**6
#
#powerData = []
#powerData1 = []
#powerData2 = []
#powerData3 = []
#powerData4 = []
#rsfq_4k = []
#rsfq_20mk = []
#cmos_4k = []
#cmos_20mk = []
#for item in cpuDataGZIP:
#	cpu_ts_val = (int(float(item)*(2.8*10**9)))
#
#	num_ops_cmos = cpu_ts_val * CMOS_ops_per_tick
#	num_ops_rsfq = cpu_ts_val * RSFQ_ops_per_tick
#
#	power_cmos = num_ops_cmos * cryoCMOS_factor
#	power_rsfq = num_ops_rsfq * RSFQ_factor 
#
#	power_cmos_4k = power_cmos * Penalty_4K
#	power_cmos_20mK = power_cmos * Penalty_20mK
#	
#	power_rsfq_4k = power_rsfq * Penalty_4K
#	power_rsfq_20mK = power_rsfq * Penalty_20mK
#
#	rsfq_4k.append(power_rsfq_4k)
#	rsfq_20mk.append(power_rsfq_20mK)
#	cmos_4k.append(power_cmos_4k)
#	cmos_20mk.append(power_cmos_20mK)
#	
#powerData1.append(rsfq_4k)
#powerData2.append(rsfq_20mk)
#powerData3.append(cmos_4k)
#powerData4.append(cmos_20mk)
#
#powerData.append(rsfq_4k)
#powerData.append(rsfq_20mk)
#powerData.append(cmos_4k)
#powerData.append(cmos_20mk)
#
#
#print "CPU Usage Data"
#print cpuDataGZIP
#print "Power Data:"
#print powerData
#
#fplot.figplot(benchName,compData,powerData1,moduleRanges,"RSFQ-4K")
#fplot.figplot(benchName,compData,powerData2,moduleRanges,"RSFQ-20mK")
#fplot.figplot(benchName,compData,powerData3,moduleRanges,"CryoCMOS-4K")
#fplot.figplot(benchName,compData,powerData4,moduleRanges,"CryoCMOS-20mK")
#
#fplot.figplot(benchName,compData,powerData,moduleRanges,"Full Suite")
#
#fp.figplot(benchName,compData,cpuData,moduleRanges,"cputs")
#fp.figplot(benchName,compData,cpuData,moduleRanges,"cpu")
#fp.figplot(benchName,memoryUsageMax,cpuData,moduleRanges,"max")
#
#with open (str(benchName + "cputs"), 'w') as f:
#	for item in cpuData:
#		for val in item:
#			f.write(str(int(numpy.ceil(val*(2.8*10**9)))) + " ")
#		f.write("\n")
#f.close()
#
#with open (str(benchName + "power_data"), 'w') as f:
#    for key,value in compData:
#        f.write(str(key))
#        f.write("\n")
#    f.write("rsfq_4k \n")
#    for item in powerData1:
#        f.write(str(item) + " ")
#        f.write("\n")
#    f.write("rsfq_20mk \n")
#    for item in powerData2:
#        f.write(str(item) + " ")
#        f.write("\n")
#    f.write("cmos_4k \n")
#    for item in powerData3:
#        f.write(str(item) + " ")
#        f.write("\n")
#    f.write("cmos_20mk \n")
#    for item in powerData4:
#        f.write(str(item) + " ")
#        f.write("\n")
#
#f.close()
#
#print "Memory Usage Statistics:"
#
##print memoryUsageStatisticsBZIP2
##print memoryUsageStatisticsSCZ
##print memoryUsageStatisticsZIP
##print memoryUsageStatisticsTAR
##print memoryUsageStatisticsGZIP
#
#
#
#
#print "[ccs][6] Data Analysis Complete" 
#print "[ccs][7] Full Suite Analysis" 


