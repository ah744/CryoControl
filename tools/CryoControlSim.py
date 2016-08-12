#!/usr/bin/python
import numpy
import scipy
import sys
import subprocess
import os
import resource
import psutil
import operator
import matplotlib.pyplot as plt

def plot(benchTitle,data,cpu_usage_data,flag):
	N = len(data)
	width = 0.8 
	domain = []
	ind = numpy.arange(N)*(len(cpu_usage_data)+1)
	print "ind:::"
	print ind
	for x in range(N):
	    domain.append(numModules-x)
	capacities = []
	decompressions = []
	if flag != "max":
		for item in reversed(data):
		    capacities.append(item[0])
		    decompressions.append(item[1])
		print "Capacities in KB:"
		capacities_kb = []
		for item in capacities:
			capacities_kb.append(item/1000)
		print capacities_kb
		print "Decompressions"
		print decompressions
	fig = plt.figure()
	ax = fig.add_subplot(111)
	if flag == "max":
		data_kb = []
		for item in data:
			data_kb.append(item/1000)
		rects1 = ax.bar(ind, data_kb, width, label= 'Max Memory Usage', color='blue')	
	else:
		rects1 = ax.bar(ind, capacities_kb, width, label= 'Cache Capacity', color='black')
	ax.set_xlim(-width,len(ind)+width)
	ax2 = ax
	if flag != "max":
		ax2 = ax.twinx()
	second_bar_data = []
	second_bar_label = '' 
	third_bar_data = []
	third_bar_label = ''
	secondRects = []
	new_bar_data = []
	colo = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
	if flag == "cpu":
		new_bar_label = 'CPU Time (Seconds)'
		for item in cpu_usage_data:
			new_bar_data = [] 
			if flag == "memory":
				for val in item:
					new_bar_data.append(val/1000000)
			else:
				new_bar_data = item
			print item
			secondRects.append(ax2.bar(ind+(width*(cpu_usage_data.index(item)+1)), new_bar_data, width, label = new_bar_label, color = colo[cpu_usage_data.index(item)] ))
	elif flag == "memory":
		new_bar_label = 'Memory Usage (KB)'
		for item in cpu_usage_data:
			new_bar_data = [] 
			if flag == "memory":
				for val in item:
					new_bar_data.append(val/1000000)
			else:
				new_bar_data = item
			print item
			secondRects.append(ax2.bar(ind+(width*(cpu_usage_data.index(item)+1)), new_bar_data, width, label = new_bar_label, color = colo[cpu_usage_data.index(item)] ))

	elif flag == "both": 
		second_bar_data = decompressions 
		second_bar_label = 'Number of Decompressions'
		third_bar_data = cpu_usage_data
		third_bar_label = 'CPU Time (Seconds)'
#		rects3 = ax2.bar(ind+(width*2), third_bar_data, width, label= third_bar_data, color='white')
	#	ax2.set_xlim(-width,len(ind)+width)
	ax.set_ylabel("Capacity (KB)")
	title = ""
	if flag == "cpu":
		ax2.set_ylabel("CPU Time (Seconds)")
		title = "CPU Time Used"
	elif flag == "decompressions":
		ax2.set_ylabel("Decompressions")
		title = "Decompressions Performed"
	elif flag == "memory":
		ax2.set_ylabel("Memory Used in Decompressions (MB)")
		title = "Memory Used by Decompression Operations"
	elif flag == "max":
		ax2.set_ylabel("Memory (KB)")
		title = "Max Memory Used by Decompression Algorithm"
	else:	
		ax2.set_ylabel("Decompressions Number/CPU Time")
		title = "CPU Time and Decompressions Performed"

	ax.set_xlabel("Number of Modules Containable by Cache")
	ax.set_title(benchTitle + "\n" + "Cache Capacities and " + title)
	xTickMarks = domain
	xTickMarks[0] = "Entire Program"
	if flag == "max":
		ax.set_title(benchTitle + "\n" + title)
		xTickMarks = ['BZIP', 'SCZ', 'ZIP', 'TAR', 'GZIP']
	ax.set_xticks(ind+width)
	xtickNames = ax.set_xticklabels(xTickMarks)
	plt.setp(xtickNames, fontsize=10)
	
	def autolabel(rects):
	    # attach some text labels
	    for rect in rects:
	        height = rect.get_height()
	        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
	                '%d' % int(height),
	                ha='center', va='bottom')
#	autolabel(secondRects[0])
	## add a legend
		#ax.legend( (rects1[0], rects2[0], rects3[0]), ('Cache Capacity', 'Decompressions', 'CPU Time (Seconds)') )
	rects = []
	rects.append(rects1[0])
	if flag == "cpu" or flag == "decompressions" or flag == "memory":
		for item in secondRects:
			rects.append(item[0])
		labs = ['Cache Capacity', "BZIP2", "SCZ", "ZIP", "TAR", "GZIP"]
	elif flag == "max":
		labs = ['Memory (KB)'] 
	ax.legend(rects, labs)
	plt.savefig(str(str(ax.title) + ".pdf"), bbox_inches="tight")


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




def setlimits():
	resource.setrlimit(resource.RLIMIT_RSS, (1000, 1000))

def compress_decompress(compressionAlgorithm,switch):
	compressionStatistics = {}
	memoryUsageStatistics = {}
	for file in os.listdir(os.getcwd()):
	    if file.endswith(".bin"):
			filename = str(file) 
			if compressionAlgorithm == "zip":
				usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
				if switch == "compress":
					p = subprocess.Popen([compressionAlgorithm, " -r", str(file + ".zip"), str(file)])
				else:
					p = subprocess.Popen([str("un"+compressionAlgorithm), str(file + ".zip")])
				ru = os.wait4(p.pid,0)[2]
				usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
				cpu_time = usage_end.ru_utime - usage_start.ru_utime
				mem_used = usage_end.ru_maxrss
				print mem_used
				print cpu_time
				memoryUsageStatistics[filename] = mem_used
				compressionStatistics[filename] = cpu_time			
			elif compressionAlgorithm == "tar":
				usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
				if switch == "compress":
				   	p = subprocess.Popen([compressionAlgorithm, "-zcvf", str(file + ".tar"), file])
				else:
				   	p = subprocess.Popen([compressionAlgorithm, "-xvf", str(file + ".tar"), file])
			   	ru = os.wait4(p.pid,0)[2]
			   	usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
			   	cpu_time = usage_end.ru_utime - usage_start.ru_utime
			   	mem_used = usage_end.ru_maxrss
			   	print mem_used
			   	print cpu_time
				memoryUsageStatistics[filename] = mem_used
			   	compressionStatistics[filename] = cpu_time			
			elif compressionAlgorithm == "scz":
				usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
				if switch == "compress":
					p = subprocess.Popen([str(compressionAlgorithm + "_compress"), file]) 
				else:
					p = subprocess.Popen([str(compressionAlgorithm + "_decompress"), str(file+".scz")])
				ru = os.wait4(p.pid,0)[2]
				usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
				cpu_time = usage_end.ru_utime - usage_start.ru_utime
				mem_used = ru.ru_maxrss 
				print mem_used
				print cpu_time
				memoryUsageStatistics[filename] = mem_used
				compressionStatistics[filename] = cpu_time			
			elif compressionAlgorithm == "gzip":
				usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
				if switch == "compress":
					p = subprocess.Popen([compressionAlgorithm,"-f", "-k", "-S", ".gzip", file]) 
				else:
					p = subprocess.Popen([compressionAlgorithm,"-f", "-d", "-k", str(file+".gzip")])
				ru = os.wait4(p.pid,0)[2]
				usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
				cpu_time = usage_end.ru_utime - usage_start.ru_utime
				mem_used = ru.ru_maxrss 
				print mem_used
				print cpu_time
				memoryUsageStatistics[filename] = mem_used
				compressionStatistics[filename] = cpu_time			
			elif compressionAlgorithm == "bzip2":
				usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
				if switch == "compress":
					p = subprocess.Popen([compressionAlgorithm, "-k","-s", "-f",file]) 
				else:
					subprocess.call(['cp', str(file+".bz2"), str(file+"bzip2")])
					p = subprocess.Popen(["bunzip2", "-k","-f","-s", str(file+".bz2")])
				ru = os.wait4(p.pid,0)[2]
				usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
				cpu_time = usage_end.ru_utime - usage_start.ru_utime
				mem_used = ru.ru_maxrss 
				print mem_used
				print cpu_time
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


print "Max Memory Usage Requirements by Compression Algorithm:"
print memoryUsageMax


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
#print "Total Number of Modules: " + str(numModules) 
#print "Sizes of Modules" + str(len(filesizes_compressed)) 
sorted_filesizes_decompressed = sorted(filesizes_decompressed.items(), key=operator.itemgetter(1))
ordered_filesizes_decompressed = []
for pair in reversed(sorted_filesizes_decompressed):
    ordered_filesizes_decompressed.append(pair)
    #print str(pair[1]) + "  " + pair[0] 
#print "Total Decompressed Module Size: " + str(sumDecompressedModules) + " Bytes"
#print "Total Compressed Module Size: " + str(sumCompressedModules) + " Bytes"
largestModuleSize = ordered_filesizes_decompressed[0][1]
#print "Largest Module Size: " + str(largestModuleSize) + "\n"

ranges = []
newValue = sumDecompressedModules
ranges.append(newValue)
for pair in sorted_filesizes_decompressed:
    #print pair[0]
    newValue -= pair[1]
    ranges.append(newValue) 
for x in ranges:
    if x < largestModuleSize:
        ranges.remove(x)
#print ranges


print "ccs[4]: Data Ranges Prepared"
print "ccs[5]: Performing Simulation"

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
	print "Simulating Capacity: " + str(capacity)
	output =  subprocess.check_output(['../cachesim', str(capacity), 'full', 'FIFO', benchName, '1'])
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



print "ccs[5]: Simulation Complete"
print "ccs[6]: Beginning Data Analysis"

#for item in compressionStatistics:
#	print item + "\t" + str(compressionStatistics[item])

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


plot("BWT",compData,memData,"memory")
plot("BWT",compData,cpuData,"cpu")
plot("BWT",memoryUsageMax,cpuData,"max")

