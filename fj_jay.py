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
    errorMat = numpy.zeros(errShape)
    
    pivotShape = (classes, numVal)
    pivotMat = numpy.ndarray(pivotShape, dtype=numpy.float32)
    
    #Initialize the arrays as globals.  PivotMat is not essential the others are.
    initVar(sharedmem_sample.SharedMemArray(varMat))
    initErr(sharedmem_sample.SharedMemArray(errorMat))
    
    del varMat, errorMat
    
    return pivotMat, numClass
	

def errPop(sharedrow, k, numVal, stop, numRow):
    #Calculate the error matrix
    varArr = sharedVar.asarray() #Get a view of D
    errArr = sharedErr.asarray() #Get a view of the error matrix
    
    for col in range(numRow, stop):
	best = numpy.inf
	right = col
	
	while right >= numRow:
	    rv = varArr[right, col]
	    e = errArr[numRow-1, right-1]
	    if rv+e < best:
		best = rv+e
	    right -= 1
	errArr[numRow,col] = best

def fj(sharedVar,i, values, start):
    #Calculate the variance matrix by row from a shared memory array
    arr = sharedVar.asarray()
    arr[i] = numpy.apply_along_axis(calcVar, 1, arr[i], len(values))
    arr[i][numpy.isnan(arr[i])] = 0 #Set the nan to 0

def calcVar(arrRow, lenValues):
    #Calculate the diameter matrix
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
    #values = numpy.arange(5000)
    numVal = len(values)

    #Allocate all necessary memory
    pivotMat, numClass = allocate(values)
    
    #Calculate the number of cores over which to multiprocess
    cores = multiprocessing.cpu_count()
    cores *= 2
    step = numVal // cores
    
    #Calculate the variance matrix
    jobs = []
    for i in range(0,len(values),step):
	p = multiprocessing.Process(target=fj, args=(sharedVar, slice(i, i+step), values, i))
	jobs.append(p)
	p.start()
	p.join()
    
    del jobs[:] #Empty the jobs list
    
    #Calculate the error matrix
    sharedErr.asarray()[0] = sharedVar.asarray()[0]

    for j in xrange(1,numClass):
	step= len(values)/cores #Naive split of the errorMat row into equal segments
	for k in range(0,len(values),step):
	    p = multiprocessing.Process(target=errPop, args=(sharedErr.asarray()[j], slice(k, k+step), numVal, k+step, j))
	    jobs.append(p)
	    p.start()
	    p.join() #Wait until all the processes per row are finished before iterating the row

    #Calculate Pivots
    pivots = []
    j = numClass - 1
    col = numVal - 1
    
    while j > 0:
	ev = sharedErr.asarray()[j, col]
	pivot_search = True
	right = col
	
	while pivot_search:
	    left_error = sharedErr.asarray()[j-1, right-1]
	    right_error = sharedVar.asarray()[right, col]
	    if left_error + right_error == ev:
		pivots.insert(0, right)
		col = right -1
		pivot_search = False
	    right -= 1
	j -=1
	
    print pivots
    
if __name__ == '__main__':
    multiprocessing.freeze_support()#For windows
    main()
    
    
    
