#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt

def figplot(benchTitle,module_sizes):
##	N = len(module_sizes)
	max_module_size = module_sizes[0][1]
	bins = []
	binvalue = max_module_size

	while binvalue > 1:
		bins.append(binvalue)
		binvalue = binvalue/2
	bins_sorted = bins[::-1]
	sizes = []
	fig = plt.figure()
	ax = fig.add_subplot(111)
	for item in module_sizes:
		sizes.append(item[1])
	counts, bins, patches = ax.hist(sizes)
	ax.set_title(benchTitle+" \n Module Size Distribution")
	ax.set_xlabel("Module Sizes (KBytes)")
	ticks = []
	ticklabels = []
	i = 1
	while i < len(bins):
		ticks.append(bins[i])
		ticklabels.append(int(bins[i])/1000)

		i = i + 1
	ticks_centered = []
	for item in ticks:
		ticks_centered.append(item)
	ax.set_xticks(ticks_centered)
	ax.set_xticklabels(ticklabels)
	ax.set_ylabel("Frequency")
	plt.savefig(str("ModuleSizeDistribution.pdf"), bbox_inches="tight")
