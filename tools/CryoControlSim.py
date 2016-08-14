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

print "------------Cryogenic Control Module Cache Simulator---------------"
#compressionAlgorithm = input("Specify Compression Algorithm: ")
compressionAlgorithm = "scz"

print "Running: " + benchName
print "ccs[0]: Performing Module Extraction"

if(not os.path.exists("Algs")):
	os.makedirs("Algs")
os.chdir("Algs")
newPathInput = "../" + fullPathInput
scriptsDir = "../../"

if(not os.path.exists(benchName)):
    os.makedirs(benchName)

os.chdir(benchName)
newPathInput = "../" + newPathInput

subprocess.call([scriptsDir + 'moduleextraction', newPathInput])
moduleFilePath = scriptsDir + algsDirectory + "/" + benchName + "modules"
subprocess.call(['mv', moduleFilePath, "."]) 

print "ccs[0]: Module Extraction Complete"
print "ccs[1]: Linking Leaf Modules"

subprocess.call([scriptsDir + 'linker'])

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
					p = subprocess.Popen(["zip", "-r", str(filename + ".zip"), str(filename)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				else:
					p = subprocess.Popen(["unzip", "-f", str(filename + ".zip")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				ru = os.wait4(p.pid,0)[2]
				usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
				cpu_time = usage_end.ru_utime - usage_start.ru_utime
				mem_used = usage_end.ru_maxrss
				memoryUsageStatistics[filename] = mem_used
				compressionStatistics[filename] = cpu_time			
			elif compressionAlgorithm == "tar":
				usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
				if switch == "compress":
				   	p = subprocess.Popen([compressionAlgorithm, "-zcvf", str(file + ".tar"), file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				else:
				   	p = subprocess.Popen([compressionAlgorithm, "-xvf", str(file + ".tar"), file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			   	ru = os.wait4(p.pid,0)[2]
			   	usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
			   	cpu_time = usage_end.ru_utime - usage_start.ru_utime
			   	mem_used = usage_end.ru_maxrss
				memoryUsageStatistics[filename] = mem_used
			   	compressionStatistics[filename] = cpu_time			
			elif compressionAlgorithm == "scz":
				usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
				if switch == "compress":
					p = subprocess.Popen([str(compressionAlgorithm + "_compress"), file], stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
				else:
					p = subprocess.Popen([str(compressionAlgorithm + "_decompress"), str(file+".scz")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				ru = os.wait4(p.pid,0)[2]
				usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
				cpu_time = usage_end.ru_utime - usage_start.ru_utime
				mem_used = ru.ru_maxrss 
				memoryUsageStatistics[filename] = mem_used
				compressionStatistics[filename] = cpu_time			
			elif compressionAlgorithm == "gzip":
				usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
				if switch == "compress":
					p = subprocess.Popen([compressionAlgorithm,"-f", "-k", "-S", ".gzip", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
				else:
					p = subprocess.Popen([compressionAlgorithm,"-f", "-d", "-k", str(file+".gzip")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				ru = os.wait4(p.pid,0)[2]
				usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
				cpu_time = usage_end.ru_utime - usage_start.ru_utime
				mem_used = ru.ru_maxrss 
				memoryUsageStatistics[filename] = mem_used
				compressionStatistics[filename] = cpu_time			
			elif compressionAlgorithm == "bzip2":
				usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
				if switch == "compress":
					p = subprocess.Popen([compressionAlgorithm, "-k","-s", "-f",file], stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
				else:
					subprocess.call(['cp', str(file+".bz2"), str(file+".bzip2")])
					p = subprocess.Popen(["bunzip2", "-k","-f","-s", str(file+".bz2")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				ru = os.wait4(p.pid,0)[2]
				usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
				cpu_time = usage_end.ru_utime - usage_start.ru_utime
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

print "ccs[2]: Module Compression Complete"
print "ccs[3]: Preparing Simulator Input Files"

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

print "ccs[3]: Simulator Inputs Prepared"
print "ccs[4]: Preparing Data Ranges"

numModules = len(filesizes_compressed)
sorted_filesizes_decompressed = sorted(filesizes_decompressed.items(), key=operator.itemgetter(1))
ordered_filesizes_decompressed = []
for pair in reversed(sorted_filesizes_decompressed):
    ordered_filesizes_decompressed.append(pair)
largestModuleSize = ordered_filesizes_decompressed[0][1]

ranges = []
newValue = sumDecompressedModules
ranges.append(newValue)
for pair in sorted_filesizes_decompressed:
    newValue -= pair[1]
    ranges.append(newValue) 
for x in ranges:
    if x < largestModuleSize:
        ranges.remove(x)


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



print "ccs[5]: Simulation Complete"
print "ccs[6]: Beginning Data Analysis"

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


def plot(benchTitle,data,cpu_usage_data,flag):
	N = len(data)
	width = 0.8 
	domain = []
	ind = numpy.arange(N)*(len(cpu_usage_data)+1)
	for x in range(N):
	    domain.append(numModules-x)
	capacities = []
	decompressions = []
	if flag != "max" and flag != "full":
		for item in reversed(data):
		    capacities.append(item[0])
		    decompressions.append(item[1])
		capacities_kb = []
		for item in capacities:
			capacities_kb.append(item/1000)
	fig = plt.figure()
	ax = fig.add_subplot(111)
	if flag == "max":
		data_kb = []
		ind = numpy.arange(N)
		for item in data:
			data_kb.append(item/1000)
		rects1 = ax.bar(ind, data_kb, width, label= 'Max Memory Usage', color='blue')	
	elif flag == "full":
		rects1 = ax.bar(ind, data, width, label= 'Max Memory Usage', color='blue')	
		
	else:
		rects1 = ax.bar(ind, capacities_kb, width, label= 'Cache Capacity', color='black')

	if flag == "max":
		ax.set_xlim(-(width/2),len(ind))
	else:
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
			new_bar_data = item
			secondRects.append(ax2.bar(ind+(width*(cpu_usage_data.index(item)+1)), new_bar_data, width, label = new_bar_label, color = colo[cpu_usage_data.index(item)] ))
	if flag == "cputs":
		new_bar_label = 'CPU Time (Timesteps)'
		for item in cpu_usage_data:
			new_bar_data = []
			new_bar_data_in = item
			for val in new_bar_data_in:
				new_bar_data.append(val*100)
			secondRects.append(ax2.bar(ind+(width*(cpu_usage_data.index(item)+1)), new_bar_data, width, label = new_bar_label, color = colo[cpu_usage_data.index(item)] ))
	elif flag == "memory":
		new_bar_label = 'Memory Usage (KB)'
		for item in cpu_usage_data:
			for val in item:
				new_bar_data.append(val/1000)
			secondRects.append(ax2.bar(ind+(width*(cpu_usage_data.index(item)+1)), new_bar_data, width, label = new_bar_label, color = colo[cpu_usage_data.index(item)] ))
	elif flag == "full":
		new_bar_label = 'Speedup'
		for item in cpu_usage_data.values():
			lengthDiff = len(data) - len(item)
			new_bar_data = item
			for x in range(lengthDiff):
				new_bar_data.append(0)	
			secondRects.append(ax2.bar(ind+(width*(cpu_usage_data.values().index(item)+1)), new_bar_data, width, label = new_bar_label, color = colo[cpu_usage_data.values().index(item)] ))
	elif flag == "both": 
		second_bar_data = decompressions 
		second_bar_label = 'Number of Decompressions'
		third_bar_data = cpu_usage_data
		third_bar_label = 'CPU Time (Seconds)'
#		rects3 = ax2.bar(ind+(width*2), third_bar_data, width, label= third_bar_data, color='white')
	#	ax2.set_xlim(-width,len(ind)+width)
	ax.set_ylabel("Capacity (KB)")
	if flag == "full":
		ax.set_ylabel("Capacity (Modules)")
	title = ""
	if flag == "cpu":
		ax2.set_ylabel("CPU Time (Seconds)")
		title = "CPU Time Used"
	if flag == "cputs":
		ax2.set_ylabel("Timesteps")
		title = "CPU Ticks (timesteps)"
	elif flag == "decompressions":
		ax2.set_ylabel("Decompressions")
		title = "Decompressions Performed"
	elif flag == "memory":
		ax2.set_ylabel("Memory Used in Decompressions (MB)")
		title = "Memory Used by Decompression Operations"
	elif flag == "max":
		ax2.set_ylabel("Memory (KB)")
		title = "Max Memory Used by Decompression Algorithm"
	elif flag == "full":
		ax2.set_ylabel("Speedup")
		ax2.set_ylim([0.98,1.02])

	ax.set_xlabel("Number of Modules Containable by Cache")
	ax.set_title(benchTitle + "\n" + "Cache Capacities and " + title)
	xTickMarks = domain
	xTickMarks[0] = "Entire Program"
	if flag == "max":
		ax.set_title(benchTitle + "\n" + title)
		xTickMarks = ['BZIP', 'SCZ', 'ZIP', 'TAR', 'GZIP']
	elif flag == "full":
		ax.set_title("Benchmark Runtimes With Limited Cache Capacities")
		for x in range(len(data)):
			xTickMarks[x] = 'N - ' + str(x)
			xTickMarks[0] = 'All'
		ax.set_xlabel("Number of Modules Containable by Cache\nN = Total Number of Modules per Benchmark")
	ax.set_xticks(ind+width+1.5)
	if flag == "max":
		ax.set_xticks(ind+0.4)
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
	if flag == "cpu" or flag == "cputs" or flag == "decompressions" or flag == "memory":
		for item in secondRects:
			rects.append(item[0])
		labs = ['Cache Capacity', "BZIP2", "SCZ", "ZIP", "TAR", "GZIP"]
	elif flag == "max":
		labs = ['Memory (KB)'] 
		ax.legend(rects, labs)
	elif flag == "full":
		for item in secondRects:
			rects.append(item[0])
		labs = ['Cache Capacity']
		for item in cpu_usage_data.keys():	
			labs.append(item[:(item.find("."))])
		ax.legend(rects,labs, bbox_to_anchor=(1,1) )
	else:
		ax.legend(rects, labs, bbox_to_anchor=(1.5, 1))
	plt.savefig(str(str(ax.title) + ".pdf"), bbox_inches="tight")

plot(benchName,compData,cpuData,"cputs")
plot(benchName,compData,cpuData,"cpu")
plot(benchName,memoryUsageMax,cpuData,"max")

with open (str(benchName + "cputs"), 'w') as f:
	for item in cpuData:
		for val in item:
			f.write(str(int(numpy.ceil(val*100))) + " ")
		f.write("\n")
f.close()

print "ccs[6] Data Analysis Complete" 
print "ccs[7] Full Suite Analysis" 

def full_suite():
	os.chdir(scriptsDir)
	if(not os.path.exists("Algs")):
	    exit(1)
	os.chdir("Algs")

	benchTS = {}
	benchCPUData = {}
	for file in os.listdir(os.getcwd()):
		os.chdir(absScriptsDir)
		if not file == ".DS_Store":
			os.chdir("../" + "Algorithms/" + file)
			with open ((file + "time"), 'r') as f:
				for line in f:
					if line.startswith("#Num of SIMD time steps for function main : "):
						lineSplit = line.split(" ")
						benchTS[file] = lineSplit[-1][:-2]
			os.chdir(absScriptsDir)
			os.chdir("Algs/"+file)
			with open ((file+"cputs"), 'r') as f:
				allData = []
				for line in f:
					allData.append(line.split(" "))
				benchCPUData[file] = (allData[-1][:-1])
	finalBenchData = {}	
	finalBenchmarkTS = []
	for benchmarkName in benchCPUData:
		bench_modified_ts = []
		alg_ts = 0
		for item in benchTS:
			if item == benchmarkName:
				alg_ts = int(benchTS[item])
		for cpu_ts in benchCPUData[benchmarkName]:
			cpu_ts = float(cpu_ts)
			alg_ts = float(alg_ts)
			bench_modified_ts.append(alg_ts/(cpu_ts+alg_ts))
		finalBenchmarkTS.append(bench_modified_ts)
		finalBenchData[benchmarkName] = bench_modified_ts 
	return finalBenchData

benchData = full_suite()
maxBenchDomain = 0
for item in benchData:
	if len(benchData[item]) > maxBenchDomain:
		maxBenchDomain = len(benchData[item])
domain_full = numpy.arange(maxBenchDomain)
domain_full_proper = []
for item in reversed(domain_full):
	domain_full_proper.append(item)

plot(benchName,domain_full_proper,benchData,"full")



