'''These are the tests that I have started to run with the iterative conversion from pure python to numpy.'''

import numpy
import timeit
import time
import multiprocessing
import sharedmem_sample

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

    '''I should populate the errMat with the min of the cumsum from index x-y and index y+1 - z'''
    
    for y in sharedrow[k]:
	print y
	print sharedrow[k]
	#i = 0
	#for x in range(0,stop):
	    #err = varArr[0][i] + varArr[i+1][stop]
	    ##print err, i, y
	    #i+=1
	    #if err <= y:
		#sharedrow[y] = err
    
    
    '''My idea here is to have a single core start to populate the first row.  Once it has hit a predetermiend point a second core can start on the second row'''
    
    
    
def fj(sharedVar,i, values, start):
    '''Calculate the variance matrix by row from a shared memory array'''
    arr = sharedVar.asarray()
    arr[i] = numpy.apply_along_axis(calcVar, 1, arr[i], len(values))
    arr[i][numpy.isnan(arr[i])] = 0 #Set the nan to 0

def calcVar(arrRow, lenValues):
    '''Calculate the diameter matrix'''
    #n is the number of elements.  These lines maintain the shape and count of n, leading 0s are added to the array.
    lenN = (arrRow != 0).sum() #Get the number of nonzero elements in the array row
    n = numpy.arange(1, lenN+1) #Generate a vector with len(values) and populate it 1-n
    
    #Only if the number of elements (n) in the Variance Matrix Row are not equal to the total number of elements
    if lenN != lenValues:
	n.resize(arrRow.shape[0]) #Reshape the n vector	
	n[arrRow.shape[0]-lenN:] =  n[:lenN-arrRow.shape[0]] #Reorder the n vector
	n[0:arrRow.shape[0]-lenN] = 0    #Set the leading elements of n to zero, where n should be 0

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
    
    '''Calculate the variance matrix'''
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
    
    '''Calculate the error matrix'''
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

    print sharedErr.asarray()
    
if __name__ == '__main__':
    multiprocessing.freeze_support()#For windows
    main()
    
    
    
