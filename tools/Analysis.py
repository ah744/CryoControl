#!/usr/bin/python
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import MaxNLocator
import numpy as np

n = 100 

SolutionSpaceFullInline = []
CodeSizeFullInline = []

def FullInline((lth, lgthPar, freq, pll)):
    size = (lth * freq - lth - freq - pll)
#    if freq == 0:
#        return 0
#    else:
    return size 

def PartialInline((lth, lthPar, freq, pll)):
#    if freq == 0:
#        return 0
    if lthPar == lth:
        return FullInline((lth, lthPar, freq, pll))
    elif pll > (freq * lthPar):
        pll = freq * lthPar
    return (lthPar * freq - lthPar - pll)

def EvaluateCodesize(space, flag):
    Codesize = []
    if flag == "full":
        for vector in space:
            Codesize.append(FullInline(vector))
    elif flag == "partial":
        for vector in space:
            Codesize.append(PartialInline(vector))
    return Codesize


def FullInlineInputs():
    SolutionSpace = []
    Codesize = []
#    for length in range(n/10,n/2+1,n/10):
    for length in range(n/10,n/10+1,10):
        for lengthParallel in range(length/4,length+1,length/4):
#        for lengthParallel in range(length/2, length/2+1, 10):
#            for frequency in range(n/length, n/length + 1, 10):
            for frequency in range(n/length+1):
                for parallelism in range(frequency*length+ 1):
#                for parallelism in range(frequency*lengthParallel/2,frequency*lengthParallel/2 + 1,10):
                    SolutionSpace.append((length,lengthParallel,frequency,parallelism))
    return SolutionSpace

def PartialInlineInputs():
    SolutionSpace = []
    Codesize = []
#    for length in range(n/10,n/2+1,n/10):
    for length in range(n/10,n/10+1,10):
        for lengthParallel in range(length/4,length+1,length/4):
#        for lengthParallel in range(length/2, length/2+1, 10):
            for frequency in range(n/length+1):
#            for frequency in range(n/length/2,n/length/2 + 1,10):
                for parallelism in range(frequency*length + 1):
#                for parallelism in range(frequency*lengthParallel/2,frequency*lengthParallel/2 + 1,10):
                    SolutionSpace.append((length,lengthParallel,frequency,parallelism))
    return SolutionSpace

def makePlot(InputsList1, InputsList2):

    SolutionSpaceFullInline = InputsList1[0] 
    CodeSizeFullInline = InputsList1[1]
    frequencies1 = [row[2] for row in SolutionSpaceFullInline]
    parallelism1 = [row[3] for row in SolutionSpaceFullInline]


    SolutionSpacePartialInline = InputsList2[0] 
    CodeSizePartialInline = InputsList2[1]
    frequencies2 = [row[2] for row in SolutionSpacePartialInline]
    parallelism2 = [row[3] for row in SolutionSpacePartialInline]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Parallelism and Frequency Sweep\nFixed module length")
    ax.set_ylabel("Codesize Change")
#    ax.set_zlabel("codesize change")
    x1 = np.array(frequencies1)
    y1 = np.array(parallelism1)
    z1 = np.array(CodeSizeFullInline)
    X1,Y1 = np.meshgrid(x1,y1)
    Z1 = z1.reshape(x1.shape)

    x2 = np.array(frequencies2)
    y2 = np.array(parallelism2)
    z2 = np.array(CodeSizePartialInline)
    X2,Y2 = np.meshgrid(x2,y2)
    Z2 = z2.reshape(x2.shape)

#    scat = ax.scatter(x1,y1,z1, c=z1, color="red", label="Full Inline", alpha=0.4)
#    scat = ax.scatter(x2,y2,z2, c=z2, color="blue", label="Partial Inline", alpha=0.4)
    scat = ax.scatter(np.arange(len(z2)), z1, label="Full Inline", color='red', alpha=0.4)
    scat2 = ax.scatter(np.arange(len(z2)),z2, label="Partial Inline", color='blue',alpha=0.4)
#    scat = ax.scatter(lengths, frequencies, parallelisms, c=codesize, cmap=plt.hot())
#    fig.colorbar(scat)
#    ax.plot_surface(X,Y,Z) 
#    surf = ax.plot_trisurf(x1,y1,z1, cmap=cm.jet, linewidth=0)
#    surf = ax.plot_trisurf(x2,y2,z2, cmap=cm.jet, linewidth=0)
#    surf = ax.plot_trisurf(lengths,frequencies,parallelisms, cmap=cm.jet, linewidth=1)
    plt.legend(loc='upper left');
    plt.show()


Set1 = FullInlineInputs()
Codesize1 = EvaluateCodesize(Set1, "full") 
print "Full Inline Inputs"
Set2 = PartialInlineInputs()
Codesize2 = EvaluateCodesize(Set2, "partial")

print "Full, \tPartial"
print "(length, length parallel, frequency, parallism)"
for i in range(len(Set1)):
    print str(Set1[i]) + "," + str(Set2[i])
    print str(Codesize1[i]) + ",\t" + str(Codesize2[i]) 


PackInputs1 = (Set1, Codesize1)
PackInputs2 = (Set2, Codesize2)

makePlot(PackInputs1, PackInputs2)
