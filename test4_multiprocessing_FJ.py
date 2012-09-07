'''These are the tests that I have started to run with the iterative conversion from pure python to numpy.'''

import numpy
import timeit
import time
import multiprocessing
import ArrayConvert

def allocate(values, classes=5, sort=True):
    if sort:
        values.sort()

    numVal = len(values)
    
    
    varShape = (numVal+1,numVal+1)
    varMat = numpy.zeros(varShape, dtype=numpy.float)
    
    errShape = (numVal+1, classes+1)
    errorMat = numpy.empty(errShape)
    errorMat[:] = numpy.NAN # This issue here is that NAN is numpy.float64.
    
    
    pivotShape = (classes+1, numVal+1)
    pivotMat = numpy.ndarray(pivotShape, dtype=numpy.float32)
    
    #Initialize the arrays as globals.  PivotMat is not essential the others are.
    init(ArrayConvert.SharedMemArray(varMat))
    
    return errorMat, pivotMat

def fj(sharedVar, i, values):
    arr = sharedVar.asarray()
    #I do not like this, but it works to get it passed in...I would likely wrap in a function for readability...
    x = str(i)
    x = int(x[6])
    x = x-1
    
    cumsum = 0
    sum_squares = 0
    
    cumsum = numpy.cumsum(values[x:]) #Get the cumulative sum of each element as an ndarray
    sum_squares = numpy.cumsum(numpy.square(values[x:]))#Get the cumulative square of each element
    n = numpy.arange(1.0,len(values[x:])+1) #Tracking numVal was really hard outside a loop so we track is in an array
    distance = sum_squares - (cumsum * (numpy.divide(cumsum, n))) #Your algorithm in numpy.

    #Here is how we can get the array size back to 'the right size and move the diameter to varMat
    distance = numpy.concatenate((numpy.zeros((arr[i].shape[1] - distance.shape[0]),),distance))
    arr[i][:] = distance
  

def init(varMat_):
    #Add the other matrices later
    global sharedVar
    sharedVar = varMat_


if __name__ == '__main__':
    multiprocessing.freeze_support()#For windows
    
    #values = numpy.asarray([12,10.8, 11, 10.8, 10.8, 10.8, 10.6, 10.8, 10.3, 10.3, 10.3, 10.4, 10.5, 10.2, 10.0, 9.9])
    #values = numpy.asarray([1,2,3,4])
    values = numpy.arange(5000)
    #Separated from FJ for timing experiments later
    #Allocation and memmove to shmemarray all in one function for comparative testing of mem footprint
    errorMat, pivotMat = allocate(values)
    
    #Multiprocessing
    jobs = []
    for i in range(len(values)): #Here I need to pass x in.  X being the step in the values array that we are currently in.
	p = multiprocessing.Process(target=fj, args=(sharedVar,slice(i, i+1), values))
	jobs.append(p)
    for job in jobs:
	job.start()
    for job in jobs:
	job.join()
    print sharedVar.asarray()
    #_fj(values)