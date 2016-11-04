#!/usr/bin/python
import numpy
import matplotlib.pyplot as plt

def figplot(benchTitle,data,cpu_usage_data,moduleRanges,flag):
	N = len(data)
	width = 0.8 
	ind = numpy.arange(N)*(len(cpu_usage_data)+1)
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
	ax.set_xlim(-width,len(ind)+width)
	if flag == "max":
		data_kb = []
		ind = numpy.arange(N)
		for item in data:
			data_kb.append(item/1000)
		rects1 = ax.bar(ind, data_kb, width, label= 'Max Memory Usage', color='blue')	
		ax.set_xlim(-(width/2),len(ind))
	else:
		rects1 = ax.bar(ind, capacities_kb, width, label= 'Cache Capacity', color='black')
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
				new_bar_data.append(int(float(val)*(2.8*10**9)))
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
	ax.set_ylabel("Capacity (KB)")
	title = ""
	if flag == "full":
		ax.set_ylabel("Capacity (Modules)")
		ax2.set_ylabel("Speedup")
	elif flag == "cpu":
		ax2.set_ylabel("CPU Time (Seconds)")
		title = "CPU Time Used"
	elif flag == "cputs":
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

	ax.set_xlabel("Number of Modules Containable by Cache")
	ax.set_title(benchTitle + "\n" + "Cache Capacities and " + title)
	xTickMarks = moduleRanges 
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
	
	rects = []
	rects.append(rects1[0])
	if flag == "cpu" or flag == "cputs" or flag == "decompressions" or flag == "memory":
		for item in secondRects:
			rects.append(item[0])
		labs = ['Cache Capacity', "BZIP2", "SCZ", "ZIP", "TAR", "GZIP"]
		ax.legend(rects,labs, bbox_to_anchor=(1.44,1) )
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
