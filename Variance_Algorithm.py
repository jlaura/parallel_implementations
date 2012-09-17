'''These are the tests that I have started to run with the iterative conversion from pure python to numpy.'''

import numpy
import timeit
import time
import multiprocessing
import sharedmem_sample
import warnings

warnings.filterwarnings('ignore', category=RuntimeWarning)

def allocate(values, classes=5, sort=False):
    numClass = classes
    if sort:
        values.sort()

    numVal = len(values)
    
    varShape = (numVal,numVal)
    varMat = numpy.zeros(varShape, dtype=numpy.float)
    
    #Preload the values in the varMat.
    for x in range(0,len(values)):
	varMat[x] = values[:]
	varMat[x][0:x] = 0

    errShape = (classes, numVal)
    errorMat = numpy.empty(errShape)
    errorMat[:] = numpy.inf # This issue here is that NAN is numpy.float64.
    
    pivotShape = (classes, numVal)
    pivotMat = numpy.ndarray(pivotShape, dtype=numpy.float32)
    
    #Initialize the arrays as globals.  PivotMat is not essential the others are.
    initVar(sharedmem_sample.SharedMemArray(varMat))
    initErr(sharedmem_sample.SharedMemArray(errorMat))
    
    del varMat, errorMat
    
    return pivotMat, numClass
	

def errPop(sharedrow, k, start, stop):
    '''
    A list of 16 items is split over 4 cores.  Each core will process
    4 columns of the error matrix in a naive split.  The first core therefore needs to 
    be able to access and calculate the minimum error for:
    
    D(0,0) + D(1,2) = x
    D(0,1) + D(2,2) = y
    
    E(2,2) = min{x,y}
    where D is the Diameter matrix, E is the error matrix, and {x,y} is a set of potential
    errors.
    
    Since we are multiprocessing and only getting a view of 1 row, we can write E as:
    E[2] = min{x,y} 
    
    because the row is constant
    '''    
    #Each core get passed a view of the sharedVar
    varArr = sharedVar.asarray()    
    
    '''My idea here is to have a single core start to populate the first row.  Once it has hit a predetermiend point a second core can start on the second row'''
    
    
    
def fj(sharedVar,i, values, start):
    
    arr = sharedVar.asarray()
    
    #All these lines do is setup the scalar n.  
    #n = numpy.arange(1,len(values[start:])+1)
    #n.resize(len(values))
    #n[start:] = n[:len(values) - start]
    #n[0:start] = 0
    
    arr[i] = numpy.apply_along_axis(calcVar, 0, arr)
    
    #rownum = 0
    #for row in arr[i]:
	#arr[i][rownum] = ((numpy.cumsum(numpy.square(row))) - ((numpy.cumsum(row)*numpy.cumsum(row)) / (n)))
	##Increment the num counter for the next row
	#n -= 1
	##Grab the next row
	#rownum+=1

def calcVar(arrRow):
    lenN = (arrRow != 0).sum() #Get the number of nonzero elements in the array row
    if lenN == 16:
	lenN = 0
    n = numpy.arange(1, lenN+1) #Generate a scalar 1-n in length with values 1-n
    n.resize(arrRow.shape[0]) #Reshape the scalar
    n[arrRow.shape[0]-lenN:] =  n[:lenN-arrRow.shape[0]]
    n[0:arrRow.shape[0]-lenN] = 0    
    return ((numpy.cumsum(numpy.square(arrRow))) - ((numpy.cumsum(arrRow)*numpy.cumsum(arrRow)) / (n)))

def initVar(varMat_):
    #Add the other matrices later
    global sharedVar
    sharedVar = varMat_

def initErr(errMat_):
    global sharedErr
    sharedErr = errMat_

def main():
    values = numpy.asarray([120,108, 110, 108, 108, 108, 106, 108, 103, 103, 103, 104, 105, 102, 100, 99])
    #values = numpy.asarray([1,2,3,4])
    #values = numpy.arange(5000)

    pivotMat, numClass = allocate(values)
    
    cores = multiprocessing.cpu_count()
    cores *= 2
    step = len(values) // cores
    
    #Calculate the variance matrix
    jobs = []
    for i in range(0,len(values),step):
	p = multiprocessing.Process(target=fj, args=(sharedVar, slice(i, i+step), values, i))
	jobs.append(p)
    for job in jobs:
	job.start()
    for job in jobs:
	job.join()

    #Empty the jobs list
    del jobs[:]
    
    #print the values of the diameter matrix
    print sharedVar.asarray()
    
    #The first row of the errMat is identical to the first row of the varMat.
    sharedErr.asarray()[0] = sharedVar.asarray()[0]
    
    #We need to iterate over each row save the first in the errorMat
    for j in xrange(1,numClass):
	step= len(values)/cores
	for k in range(0,len(values),step):
	    p = multiprocessing.Process(target=errPop, args=(sharedErr.asarray()[j], slice(k, k+step), k, k+step))
	    jobs.append(p)
	    
    for job in jobs:
	job.start()
    for job in jobs:
	job.join()

if __name__ == '__main__':
    multiprocessing.freeze_support()#For windows
    main()
    
    
    
