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
    
    
def fj(sharedVar,i, values, start):
    #Get a view of the rows to be worked on
    arr = sharedVar.asarray()
    
    #Setup the counter for the number of values
    n = numpy.arange(1,len(values[start:])+1)
    #Resize the counter and get it set up with teh correct num of preceeding zeros
    n.resize(len(values))
    n[start:] = n[:len(values) - start]
    n[0:start] = 0
    
    #Populate the array with the cumulative sum by row!
    rownum = 0
    for row in arr[i]:
	arr[i][rownum] = ((numpy.cumsum(numpy.square(row))) - ((numpy.cumsum(row)*numpy.cumsum(row)) / (n)))
	#Increment the num counter for the next row
	n -= 1
	#Clean out the negative numbers and clip to 0
	n = numpy.clip(n,0, len(values)) 
	#Grab the next row
	rownum+=1
	
	'''
	arr[i][rownum] 
	---------------
	[i] - returns the slice of the shared array at the individual core has access too.  This is a multirow (multidimensional) array.
	[rownum] - returns the specified row from the multirow view.  This is a scalar.
	arr[i][rownum][0] - would return the first value (index 0) from the view of the row.
	
	In essence this is traditional slicing plus one extra operator for rows.
	
	Here is what row #1 returns using the doctest values:
	
	row = [  99.  100.  102.  103.  103.  103.  104.  105.  106.  108.  108.  108. 108.  108.  110.  120.] 
	cumsum = [   99.   199.   301.   404.   507.   610.   714.   819.   925.  1033. 1141.  1249.  1357.  1465.  1575.  1695.] 
	sum_squares = [   9801.   19801.   30205.   40814.   51423.   62032.   72848.   83873. 95109.  106773.  118437.  130101.  141765.  153429.  165529.  179929.]
	n = [ 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16]
	
	We can calculate variance using:
	
	for x in data:
	    n = n + 1
            Sum = Sum + x
            Sum_sqr = Sum_sqr + x*x
 
	variance = (Sum_sqr - ((Sum*Sum)/n))/(n)
	
	This works for a single value in a scalar of values.
	
	Plugging in row[x], where x is the first value in the row above: 
	for 99 in data:
	    n = 0 + 1 
	    99 = 0 + 99
	    9801 = 0 + 99 * 99
	    
	variance = (9801 - ((99*99)/1)/1
	variance = 0 #Which makes sense, it is the variance of a single number...
	
	for 99, 100 in data:
	    n = 1+1
	    199 = 99 + 100 #Cumsum
	    19801 = 9801 + (100*100) #This is the sqare of the new value plus the cumulative sum of squares
	    
	variance = (19801 - ((199*199)/2)/2
	variance = 0.25
	
	for 99,100,102 in data:
	    n = 3
	    301 = 199+102 #CumSum
	    30205 = 19801 + (102*102) #CumSum of Value^2
	variance = (30205 - ((301*301)/3))/3
	variance = 1.5555555555556
	
	Output of the first row of the algorithm (scalar):
	[  0.           0.25         1.55555556   2.5          2.64         2.55555556
            2.85714286   3.484375     4.39506173   6.41         7.65289256
	    8.40972222   8.85207101   9.08673469  10.26666667  22.80859375]
	    
	'''

def initVar(varMat_):
    #Add the other matrices later
    global sharedVar
    sharedVar = varMat_

def initErr(errMat_):
    global sharedErr
    sharedErr = errMat_

def main():
    #values = numpy.asarray([120,108, 110, 108, 108, 108, 106, 108, 103, 103, 103, 104, 105, 102, 100, 99])
    #values = numpy.asarray([1,2,3,4])
    values = numpy.arange(5000)
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

    #Empty the jobs list
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

if __name__ == '__main__':
    multiprocessing.freeze_support()#For windows
    main()
    
    
    
