'''These are the tests that I have started to run with the iterative conversion from pure python to numpy.'''

import numpy
import time
import timeit
     
def _jay_fj(values, classes=5, sort=True):
    #values = numpy.random.randint(0,1000,size=(10,1))

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
    
    #varMat row counter
    x = 0
    for row in range(1, len(values)+1): #Feed this into a pool of workers row by row and no need for any for loops. How do we count x is the only issue.
	
	cumsum = 0
	sum_squares = 0
	
	cumsum = numpy.cumsum(values[x:]) #Get the cumulative sum of each element as an ndarray
	sum_squares = numpy.cumsum(numpy.square(values[x:]))	#Get the cumulative square of each element
	n = numpy.arange(1.0,len(values[x:])+1) #Tracking numVal was really hard outside a loop so we track is in an array
	distance = sum_squares - (cumsum * (numpy.divide(cumsum, n))) #Your algorithm in numpy.

	#Here is how we can get the array size back to 'the right size and move the diameter to varMat
	distance = numpy.concatenate((numpy.zeros((varMat[row].shape[0] - distance.shape[0]),),distance))
	varMat[row][:] = distance
	
	'''I would love to chat about why we are making matrices (old code) with n+1 rows and columns when it seems that
	n x n would be sufficient.  Does it have to do with 0 vs 1 based counting?  I have not dug into the error matrix yet, 
	so that could be the reason as well.'''
	
	#Increment the counter
	x+=1
	
	#I do not understand the error matrix well enough to get it populated properly.  On my todo for Thursday.
	#Using [1,2,3,4] it looks like I can simply rotate the second row of the varMat vertically and put it into the 2nd column
	# of the errorMat...it can't be that easy though!

    print varMat
	    
values = numpy.asarray([12,10.8, 11, 10.8, 10.8, 10.8, 10.6, 10.8, 10.3, 10.3, 10.3, 10.4, 10.5, 10.2, 10.0, 9.9])
#_fisher_jenks(values)
_jay_fj(values)