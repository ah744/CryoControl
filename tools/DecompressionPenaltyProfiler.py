#!/usr/bin/python
import numpy
import scipy
import sys
import subprocess
import os
import time
import resource
import psutil
import shutil
import operator
import matplotlib.pyplot as plt
import FigurePlot as fp 
import FigPlot as fplot 
import HistogramPlot as hp 
import FullSuite as fs


def compress_decompress(compressionAlgorithm,switch):
	compressionStatistics = {}
	memoryUsageStatistics = {}
	for file in os.listdir(os.getcwd()):
	    if file.endswith(".txt"):
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


def compress_loop():
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
    compressionStatistics = []
    compressionStatistics.append(compressionStatisticsBZIP2)
    compressionStatistics.append(compressionStatisticsSCZ)
    compressionStatistics.append(compressionStatisticsZIP)
    compressionStatistics.append(compressionStatisticsTAR)
    compressionStatistics.append(compressionStatisticsGZIP)
    return compressionStatistics



i = 0
while i < 33:
    compressionStatisticsBZIP2 = compress_loop()[0]
    compressionStatisticsSCZ= compress_loop()[1]
    compressionStatisticsZIP= compress_loop()[2]
    compressionStatisticsTAR= compress_loop()[3]
    compressionStatisticsGZIP= compress_loop()[4]
    size = os.path.getsize("test.txt") 

    with open("BZIP2", "a") as f:
        for key,val in compressionStatisticsBZIP2.iteritems():
            f.write(key + "\t" + str(val) + "\t")
            f.write(str(size)+"\n")
        f.close()
    with open("SCZ", "a") as f:
        for key,val in compressionStatisticsSCZ.iteritems():
            f.write(key + "\t" + str(val) + "\t")
            f.write(str(size)+"\n")
        f.close()
    with open("ZIP", "a") as f:
        for key,val in compressionStatisticsZIP.iteritems():
            f.write(key + "\t" + str(val) + "\t")
            f.write(str(size)+"\n")
        f.close()
    with open("TAR", "a") as f:
        for key,val in compressionStatisticsTAR.iteritems():
            f.write(key + "\t" + str(val) + "\t")
            f.write(str(size)+"\n")
        f.close()
    with open("GZIP", "a") as f:
        for key,val in compressionStatisticsGZIP.iteritems():
            f.write(key + "\t" + str(val) + "\t")
            f.write(str(size)+"\n")
        f.close()

    shutil.copyfile("test.txt", "base.in")
    with open("test.txt", "a") as test, open("base.in", "r") as base:
        lines = base.read()
        test.write(lines)
        test.close()
        base.close()


	os.remove("test.txt.bz2")
	os.remove("test.txt.gzip")
	os.remove("test.txt.zip")
	os.remove("test.txt.bzip2")
	os.remove("test.txt.scz")
	os.remove("test.txt.tar")
    compress_loop()
    i = i + 1

