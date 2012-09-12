'''These are the tests that I have started to run with the iterative conversion from pure python to numpy.'''

import numpy
import timeit
import time
import multiprocessing
import sharedmem_sample

def allocate(values, classes=5, sort=True):
    numClass = classes
    if sort:
        values.sort()

    numVal = len(values)
    
    varShape = (numVal+1,numVal+1)
    varMat = numpy.zeros(varShape, dtype=numpy.float)
    
    errShape = (numVal, classes)
    errorMat = numpy.empty(errShape)
    errorMat[:] = numpy.NAN # This issue here is that NAN is numpy.float64.
    
    pivotShape = (classes+1, numVal+1)
    pivotMat = numpy.ndarray(pivotShape, dtype=numpy.float32)
    
    #Initialize the arrays as globals.  PivotMat is not essential the others are.
    initVar(sharedmem_sample.SharedMemArray(varMat))
    initErr(sharedmem_sample.SharedMemArray(errorMat))
    
    del varMat, errorMat
    
    return pivotMat, numClass

def calcSlices(numVal, cores):
    #Create a list of tuples where the ideal breakdown is calculated.
    slices = []
    interval = len(numVal) / cores
    start = 0
    for i in range(start,len(numVal),interval):
	print i
	tple = ()
	

def fj(sharedVar, i, values): #Check in DocTest for _fj() p.137 DocTest was for #4
    arr = sharedVar.asarray()
    #I do not like this, but it works to get it passed in...I would likely wrap in a function for readability...
    x = str(i)
    x = int(x[6])
    x = x-1

    cumsum = numpy.cumsum(values[x:])  #Get the cumulative sum of each element as an ndarray
    sum_squares = numpy.cumsum(numpy.square(values[x:]))#Get the cumulative square of each element
    n = numpy.arange(1.0,len(values[x:])+1) #Tracking numVal was really hard outside a loop so we track is in an array
    distance = sum_squares - (cumsum * (numpy.divide(cumsum, n))) #Your algorithm in numpy.

    #Here is how we can get the array size back to 'the right size and move the diameter to varMat
    distance = numpy.concatenate((numpy.zeros((arr[i].shape[1] - distance.shape[0]),),distance))
    arr[i][:] = distance

    
    #After the varMat is populated the first row can be copied to the variance matrix
    '''
    Then the error matrix can be calculated in parallel.
    1. Cleanup the varMatrix - Added to allocate function
    2. Move the error matrix into shared memory space. - Added to allocate function
    3. Pass a single row in to divide over the number of cores
    4. Pass each core a subset of the columns
    5. Calculate the lowest variance between each combination by referencing the diameter matrix
    6. Populate the cell value with the ideal variance
    7. Iterate the row
    8. Num rows = num classes
    '''
    
    #How can we work only on the diagonal.  
    
    '''
    First row is n-1, second is n-2, n*n-1 / 2 is the total length.
    '''

def initVar(varMat_):
    #Add the other matrices later
    global sharedVar
    sharedVar = varMat_

def initErr(errMat_):
    global sharedErr
    sharedErr = errMat_

if __name__ == '__main__':
    multiprocessing.freeze_support()#For windows
    
    #values = numpy.asarray([12,10.8, 11, 10.8, 10.8, 10.8, 10.6, 10.8, 10.3, 10.3, 10.3, 10.4, 10.5, 10.2, 10.0, 9.9])
    #values = numpy.asarray([1,2,3,4])
    values = numpy.arange(5000)
    #Separated from FJ for timing experiments later
    #Allocation and memmove to shmemarray all in one function for comparative testing of mem footprint
    pivotMat, numClass = allocate(values)
    
    cores = multiprocessing.cpu_count()
    cores *= 2
    step = len(values) // cores
    #Multiprocessing
    jobs = []
    for i in range(0,len(values),step): #Here I need to pass x in.  X being the step in the values array that we are currently in.
	p = multiprocessing.Process(target=fj, args=(sharedVar,slice(i, i+step), values))
	jobs.append(p)
    for job in jobs:
	job.start()
    for job in jobs:
	job.join()
    
    #Empty the jobs list
    del jobs[:]

    #We need to iterate over each row in the errorMat
    for j in xrange(0,numClass):
	#It is not possible to index the sharedmem array, so pass an index of the view.  Slice is the slice of the row to look at.  This is naive, with each core getting the same num of Nan to work with.
	#TODO - Figure out the algorithm for the optimal breakdown in values between x cores.  The farther into the array, the longet the processing will be as additional potential combinations are tested.
	slices = calcSlices(len(values), cores)
	for k in slices:
	    p = multiprocessing.Process(target=errPop, args=(sharedErr.asarray()[j], slice(k, k+step)))
	print sharedErr.asarray()[j][0:7]

    print sharedVar.asarray()
    #_fj(values)