import numpy
import timeit
import time
import multiprocessing
import ctypes
import warnings

#profiling
import resource

#Suppress the divide by zero errors
warnings.filterwarnings('ignore', category=RuntimeWarning)

def allocate(values, classes):
    '''This function allocates memory for the variance matrix, error matrix, 
    and pivot matrix.  It also moves the variance matrix and error matrix from
    numpy types to a ctypes, shared memory array.'''
    
    numClass = classes
    numVal = len(values)
    
    varCtypes = multiprocessing.RawArray(ctypes.c_double, numVal*numVal)
    varMat = numpy.frombuffer(varCtypes)
    varMat.shape = (numVal,numVal)
    
    for x in range(0,len(values)):
	varMat[x] = values[:]
	varMat[x][0:x] = 0

    errCtypes = multiprocessing.RawArray(ctypes.c_double, classes*numVal)
    errorMat = numpy.frombuffer(errCtypes)
    errorMat.shape = (classes, numVal)
    
    pivotShape = (classes, numVal)
    pivotMat = numpy.ndarray(pivotShape, dtype=numpy.float)
    
    #Initialize the arrays as globals.
    initArr(varMat, errorMat)
    
    return pivotMat, numClass

def initArr(varMat_, errorMat_):
    '''Initialize the ctypes arrays as global variables for multiprocessing'''
    global sharedVar
    sharedVar = varMat_
    
    global sharedErr
    sharedErr = errorMat_

def fj(sharedVar,i, values, start):
    '''This function facilitates passing multiple rows to each process and
    then performing multiple vector calculations along individual rows.'''
    arr = sharedVar
    arr[i] = numpy.apply_along_axis(calcVar, 1, arr[i], len(values))
    arr[i][numpy.isnan(arr[i])] = 0

def calcVar(arrRow, lenValues):
    '''This function calculates the diameter matrix.  It is called by fj.
    The return line performs the calculation.  All other lines prepare an
    order vector, prepended with zeros when necesary which stores n, the number 
    of elements summed for each index.'''
    
    lenN = (arrRow != 0).sum()
    n = numpy.arange(1, lenN+1)
    
    if lenN != lenValues:
        n.resize(arrRow.shape[0]) 	
	n[arrRow.shape[0]-lenN:] =  n[:lenN-arrRow.shape[0]] 
	n[0:arrRow.shape[0]-lenN] = 0 

    return ((numpy.cumsum(numpy.square(arrRow))) - \
            ((numpy.cumsum(arrRow)*numpy.cumsum(arrRow)) / (n)))

def fisher_jenks(values, classes=5, sort=True):
    
    if sort:
	#pass
	values.sort()
	
    numVal = len(values)

    #Allocate all necessary memory
    pivotMat, k = allocate(values, classes)
    
    #Calculate the number of cores over which to multiprocess
    cores = multiprocessing.cpu_count()
    cores *= 2
    step = numVal // cores

    t0 = time.time()
    
    #Calculate the variance matrix
    jobs = []
    for i in range(0,len(values),step):
	p = multiprocessing.Process(target=fj,args=(sharedVar,slice(i, i+step),values, i))
	jobs.append(p) 
    for job in jobs:
	job.start()
    for job in jobs:
	job.join()
    del jobs[:], p

    t1 = time.time()

    #Calculate the error matrix
    sharedErr[0] = sharedVar[0]
    
    #Error Matrix Calculation
    row = 1
    for x in sharedErr[1:]:
	errRow = x[row:]
	for y in range(0,len(errRow)):
	    errRow[y] = numpy.amin(sharedErr[row-1][row-1:y+row] + sharedVar[:,y+row][row:y+row+1])
	row += 1
    t2 = time.time()

    #Calculate Pivots
    pivots = []
    j = k - 1
    col = numVal - 1
    
    while j > 0:
	ev = sharedErr[j, col]
	pivot_search = True
	right = col
	
	while pivot_search:
	    left_error = sharedErr[j-1, right-1]
	    right_error = sharedVar[right, col]
	    if left_error + right_error == ev:
		pivots.insert(0, right)
		col = right -1
		pivot_search = False
	    right -= 1
	j -=1
    
    t3 = time.time()
    m = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
	
    print "Pivots: ", pivots
    return (t1-t0, t2-t1, t3-t2, t3-t0,m)

#Not called by time_test.py
if __name__ == '__main__':
    
    #values = numpy.arange(4000)
    values = ([120,108, 110, 108, 108, 108, 106, 108, 103, 103, 103, 104, 105, 102, 100, 99])
    fisher_jenks(values)
    
    