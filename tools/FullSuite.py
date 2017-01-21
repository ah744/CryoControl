#!/usr/bin/python
import numpy
import sys
import subprocess
import os
import matplotlib.pyplot as plt

def plot(data,cpu_usage_data,flag):
	N = len(data)
	width = 0.8 
	ind = numpy.arange(N)*(len(cpu_usage_data)+1)
	capacities = []
	fig = plt.figure()
	ax = fig.add_subplot(111)
	rects1 = ax.bar(ind, data, width, label= 'Capacity', color='black')	
	ax.set_xlim(-width,len(ind)+width)
	ax2 = ax
	ax2 = ax.twinx()
	second_bar_data = []
	second_bar_label = '' 
	secondRects = []
	new_bar_data = []
	colo = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
	new_bar_label = 'Speedup'
	for item in cpu_usage_data.values():
		lengthDiff = len(data) - len(item)
		new_bar_data = item
		for x in range(lengthDiff):
			new_bar_data.append(0)	
		secondRects.append(ax2.bar(ind+(width*(cpu_usage_data.values().index(item)+1)), new_bar_data, width, label = new_bar_label, color = colo[cpu_usage_data.values().index(item)] ))
	ax.set_ylabel("Capacity (Modules)")
	title = ""
	ax2.set_ylabel("Speedup")
#	ax2.set_ylim(0,0.001)
	ax.set_xlabel("Number of Modules Containable by Cache")
	xTickMarks = ["Entire Program", "5/6", "2/3", "1/2", "1/3", "8", "4", "2", "1"] 
	ax.set_title("Benchmark Runtimes With Limited Cache Capacities")
	ax.set_xlabel("Number of Modules Containable by Cache\nFractions are w.r.t Total Number of Modules")
	ax.set_xticks(ind+width+1.5)
	ax.set_xlim(0,36)
	xtickNames = ax.set_xticklabels(xTickMarks)
	plt.setp(xtickNames, fontsize=10)
	def autolabel(rects):
	    # attach some text labels
	    for rect in rects:
	        height = rect.get_height()
	        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
	                '%d' % int(height),
	                ha='center', va='bottom')
	rects = []
	rects.append(rects1[0])
	for item in secondRects:
		rects.append(item[0])
	labs = ['Cache Capacity']
	for item in cpu_usage_data.keys():	
		labs.append(item[:(item.find("."))])
	ax.legend(rects,labs, bbox_to_anchor=(1,1) )
	plt.savefig(str(str(ax.title) + ".pdf"), bbox_inches="tight")

def returnAppShort(filename):
    prefix = ""
    suffix = ""
    if "flat010k" in filename:
        prefix = "10K_Flattened/"
    elif "flat2M" in filename:
        prefix = "2M_Flattened/"
    if filename.startswith("binary"):
        suffix = "BWT/"
    elif filename.startswith("boolean"):
        suffix = "BF/"
    elif filename.startswith("class"):
        suffix = "CN/"
    elif filename.startswith("ground"):
        suffix = "GSE/"
    elif filename.startswith("ising"):
        suffix = "Ising/"
    elif filename.startswith("shors"):
        suffix = "Shors/"
    elif filename.startswith("square"):
        suffix = "Square_Root/"
    elif filename.startswith("triangle"):
        suffix = "TFP/"

    return prefix+suffix



def full_suite():
    benchName = "Full App Suite"
    print "------------" + benchName + "----------"
    toolsDir = os.path.abspath(os.getcwd())
    if(not os.path.exists("Algs")):
        exit(1)
    os.chdir("Algs")
    benchTS = {}
    benchCPUData = {}
    for file in os.listdir(os.getcwd()):
		appShort = returnAppShort(file)
		print "Processing App: " + appShort + file
		os.chdir(toolsDir)
		if not file == ".DS_Store":
			if not file.startswith("shors"):
				if os.path.isdir("../"+"Algorithms/"+ appShort):
					os.chdir("../" + "Algorithms/" + appShort)
			    	with open ((file + "lpfs"), 'r') as f:
						print "\t Finding Runtime"
						for line in f:
							if line.startswith("#Num of SIMD time steps for function main : "):
								lineSplit = line.split(" ")
								benchTS[file] = lineSplit[-1][:-2]
								print "\t Runtime: " + str(lineSplit[-1][:-2])
			    	os.chdir(toolsDir + "/Algs/"+file)
			    	if os.path.isfile(file+"cputs"):
			    		print "\t Finding Decompression Time"
			    		with open ((file+"cputs"), 'r') as f:
			    			allData = []
			    			for line in f:
			    				allData.append(line.split(" "))
			    			benchCPUData[file] = (allData[-1][:-1])
			    			print "\t CPU Time: " + str(allData[-1][:-1])
			    	else:
			    		print "Omitting application: " + file 
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
