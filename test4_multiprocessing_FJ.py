'''These are the tests that I have started to run with the iterative conversion from pure python to numpy.'''

import numpy
import timeit
import time
import multiprocessing
import sharedmem_sample
from itertools import combinations

def allocate(values, classes=5, sort=True):
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
    '''This works, but I need to clean the Diameter matrix first, failed the pseudo doc test I did and turned into a total rework.  At least I'm much more versed in slicing, indexing, and broadcasting.'''
    #TODO - How can I access the PySal doctests??
    
    

    '''
    For example, a list of 16 items is split over 4 cores.  Each core will process
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
    #for col in range(0,stop):
	#right = stop
	#print col, varArr[0][col]
	#err = varArr[0][col] + varArr[col+1][stop]

	#If the calculated error is less than the existing value, use the minimum.
	#if err < sharedrow[start]:
	    #sharedrow[col] = err
	    #print sharedrow
    #x is the column that we are in at the moment
    #D = varArr[]
    

    #col += 1
    

    
    #Each core needs to know where it is starting.
    
def fj(sharedVar,i, values, start): #Check in DocTest for _fj() p.137 DocTest was for #4
    arr = sharedVar.asarray()
    n = numpy.arange(1,len(values[start:])+1)
    n.resize(16)
    n[start:] = n[:len(values) - start]
    n[0:start] = 0

    #Populate the array with the cumulative sum
    rownum = 0
    for row in arr[i]:
	arr[i][rownum] = numpy.cumsum(row)
	arr[i][rownum] = (numpy.cumsum(numpy.square(row))) - (arr[i][rownum] * (arr[i][rownum] /n ))
	#n is not pushing the right direction here...
	rownum+=1
    #sum_squares = numpy.cumsum(numpy.square(values[start:]))
     #Tracking numVal was really hard outside a loop so we 
    #distance = sum_squares - (cumsum * (cumsum /n)) #Your algorithm in numpy.
    #distance = numpy.concatenate((numpy.zeros((arr.shape[1] - distance.shape[0]),),distance))
    #arr[:] = distance

    
    #After the varMat is populated the first row can be copied to the variance matrix
    '''
    Then the error matrix can be calculated in parallel.
    1. Cleanup the varMatrix - Added to allocate function
    2. Move the error matrix into shared memory space. - Added to allocate function
    3. Pass a single row in to divide over the number of cores - Added to the slices function.
    4. Pass each core a subset of the columns - Added just prior to multiprocessing
    5. Calculate the lowest variance between each combination by referencing the diameter matrix
    6. Populate the cell value with the ideal variance
    7. Iterate the row
    8. Num rows = num classes
    '''
    
    #How can we work only on the diagonal.  
    
    '''
    First row is n-1, second is n-2, n*n-1 / 2 is the total length.  This is how we can read stright from the input format to a ctypes array.
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
    
    values = numpy.asarray([120,108, 110, 108, 108, 108, 106, 108, 103, 103, 103, 104, 105, 102, 100, 99])
    #values = numpy.asarray([1,2,3,4])
    #values = numpy.arange(5000)
    #Separated from FJ for timing experiments later
    #Allocation and memmove to shmemarray all in one function for comparative testing of mem footprint
    pivotMat, numClass = allocate(values)
    
    cores = multiprocessing.cpu_count()
    #cores *= 2
    step = len(values) // cores
    #Multiprocessing
    jobs = []
    for i in range(0,len(values),step):
	p = multiprocessing.Process(target=fj, args=(sharedVar, slice(i, i+step), values, i))
	jobs.append(p)
    for job in jobs:
	job.start()
    for job in jobs:
	job.join()
    
    ##Empty the jobs list
    #del jobs[:]
    #print sharedVar.asarray()
    ##The first row of the errMat is identical to the first row of the varMat.
    #sharedErr.asarray()[0] = sharedVar.asarray()[0]
    
    ##We need to iterate over each row save the first in the errorMat
    #for j in xrange(1,numClass):
	#step= len(values)/cores
	#for k in range(0,len(values),step):
	    #p = multiprocessing.Process(target=errPop, args=(sharedErr.asarray()[j], slice(k, k+step), k, k+step))
	    #jobs.append(p)
	    
    #for job in jobs:
	#job.start()
    #for job in jobs:
	#job.join()

    #print sharedVar.asarray()
    #_fj(values)
    
