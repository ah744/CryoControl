#!/usr/bin/python
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import MaxNLocator
import numpy as np

n = 10 

SolutionSpaceFullInline = []
CodeSizeFullInline = []

def FullInline((lth, freq, pll)):
    size = (lth * freq - lth - freq - pll)
    return size 

def PartialInline((lth, freq, pll)):
    size = (lth * freq - lth - pll)
    return size

def FullInlineInputs():
    SolutionSpace = []
    Codesize = []
    for length in range(1,n):
        for frequency in range(n/length + 1):
            for parallelism in range(frequency*length + 1):
                SolutionSpace.append((length,frequency,parallelism))
    for vector in SolutionSpace:
        Codesize.append(FullInline(vector)) 
    print SolutionSpace
    print Codesize
    return (SolutionSpace, Codesize)

def PartialInlineInputs():
    SolutionSpace = []
    Codesize = []
    for length in range(1,n):
        for frequency in rane():
            for parallelism in range():
                SolutionSpace.append((length,frequency,parallelism))
    for vector in SolutionSpace:
        Codesize.append(PartialInline(vector))
    print SolutionSpace
    print Codesize
    return (SolutionSpace, Codesize)

def makePlot(lengths,frequencies,parallelisms,Codesize):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel("length of module")
    ax.set_ylabel("frequency of module")
    ax.set_zlabel("parallelism of module")
    x = np.array(lengths)
    y = np.array(frequencies)
    z = np.array(parallelisms)
    X,Y = np.meshgrid(x,y)
    Z = z.reshape(x.shape)
    scat = ax.scatter(lengths, frequencies, parallelisms, c=Codesize, cmap=plt.hot())
#    ax.plot_surface(X,Y,Z) 
#    surf = ax.plot_trisurf(x,y,z, cmap=cm.jet, linewidth=0)
#    surf = ax.plot_trisurf(lengths,frequencies,parallelisms, cmap=cm.jet, linewidth=1)
    fig.colorbar(scat)
    
    ax.xaxis.set_major_locator(MaxNLocator(5))
    ax.yaxis.set_major_locator(MaxNLocator(6))
    ax.zaxis.set_major_locator(MaxNLocator(5))
    
#    fig.tight_layout()
    plt.show()

SolutionSpaceFullInline = FullInlineInputs()[0] 
CodeSizeFullInline = FullInlineInputs()[1]
lengths = [row[0] for row in SolutionSpaceFullInline]
frequencies = [row[1] for row in SolutionSpaceFullInline]
parallelisms = [row[2] for row in SolutionSpaceFullInline]

makePlot(lengths,frequencies,parallelisms,CodeSizeFullInline)
