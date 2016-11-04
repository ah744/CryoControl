#!/usr/bin/python
import sys
import subprocess
import os
import resource

usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
p = subprocess.Popen(["./dummy.py"])
ru = os.wait4(p.pid,0)[2]
usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
print usage_end.ru_utime - usage_start.ru_utime
