#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt

def figplot(benchTitle,cap_data,data,moduleRanges,params):
	N = len(cap_data)
	fig = plt.figure()
	width=0.8
	ax = fig.add_subplot(111)
	ax2 = ax.twinx()
	ind = np.arange(N)*(len(data)+1)
	print "ind = "
	print ind
	if params == "Full Suite":
		ax.set_title(benchTitle+" \n Power Overhead Required By Control Unit Computation")
	else:
		ax.set_title(benchTitle+" \n Power Overhead Required By Control Unit Computation"+"\n"+params)
	ax.set_xlabel("Cache Capacities (Modules)")
#	ax.set_xlim(-width,len(ind)+width)
	rects = []
	labels = ['Cache Capacity', 'RSFQ-4K', 'RSFQ-20mK', 'cryoCMOS-4K', 'cryoCMOS-20mK']
	colo = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
	capacities = []
	for item in reversed(cap_data):
	    capacities.append(item[0])
	capacities_kb = []
	for item in capacities:
		capacities_kb.append(item/1000)

	print "capacities"
	print capacities
	rects1 = ax.bar(ind, capacities, width, label = 'Cache Capacity', color='black')
	rects.append(rects1)
	i=0
	while i < len(data):
		rects2 = ax2.bar(ind+(width*i+1), data[i], width, label = "Power Requirement", color = colo[i] )
#		rects2 = ax2.bar(ind, data[i], width, label= labels[i], color=colo[i])
		rects.append(rects2)
		i = i + 1
	ax.set_ylabel("Capacity (Bytes)")
	ax2.set_ylabel("Power Overhead (W)")
	ax2.set_yscale('log')
	xTickMarks = moduleRanges 
	xTickMarks[0] = "All"
	xtickNames = ax.set_xticklabels(xTickMarks)
	print "setting xticks with labels:"
	print moduleRanges
	plt.xticks(ind)
	ax.legend(rects, labels, bbox_to_anchor=(1.5, 1))
	plt.savefig(str(params+"_PowerOverheads.pdf"), bbox_inches="tight")
