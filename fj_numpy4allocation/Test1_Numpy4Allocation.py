'''These are the tests that I have started to run with the iterative conversion from pure python to numpy.'''

import numpy
import time
import timeit

def _fisher_jenks(classes=5, sort=True):
    values = numpy.random.randint(0,1000,size=(5000,1))

    if sort:
        values.sort()

    numVal = len(values)
    
    varMat = (numVal+1)*[0] 
    for i in range(numVal+1):
        varMat[i] = (numVal+1)*[0]
        
    errorMat = (numVal+1)*[0]
    for i in range(numVal+1):
        errorMat[i] = (classes+1)*[float('inf')]
   
    pivotMat = (numVal+1)*[0]
    for i in range(numVal+1):
        pivotMat[i] = (classes+1)*[0]

    for i in range(1, numVal+1):
        sumVals = 0
        sqVals = 0
        numVals = 0

        for j in range(i, numVal+1):
            val = float(values[j-1]) 
            sumVals += val 
            sqVals += val * val 
            numVals += 1.0 
            varMat[i][j] = sqVals - sumVals * sumVals / numVals 
            if i == 1:
                errorMat[j][1] = varMat[i][j]
                
def _jay_fj(classes=5, sort=True):
    values = numpy.random.randint(0,1000,size=(5000,1))

    if sort:
        values.sort()

    numVal = len(values)
    
    '''Build an array that is [numVal by numVal (ignoring the potential improvment by leveraging sym.)].
    
    This stores the diameter matrices once calculated.
    
    For each value (n) we generate a row n x 1 which, stores the cumulative sum of squares between element[0] and each subsequent element, such that each row corresponds to each sorted numVal.  Each array is populated such at array[0,1] is the sum of squares between n0 and n1, array[0,2] is the sum of squares between n0 and n2, etc.
    
    For each dimension n is incremented by 1 (unless we sample)
    
    '''
    
    varShape = (numVal+1,numVal+1)
    varMat = numpy.zeros(varShape, dtype=numpy.float)
    
    '''Build an array that is [classes by numVal].

        This stores the error, with the first line being meaningless as it is simply the optimal error in the classes.  The subsequent lines are important though, because the last column of each row (last element) is the optimal error for that class.    
    '''
    errShape = (numVal+1, classes+1)
    errorMat = numpy.empty(errShape)
    errorMat[:] = numpy.NAN # This issue here is that NAN is numpy.float64.
    
    '''
    All the good stuff ends up here...These are going to be the pivots in the data
    '''
    
    pivotShape = (classes+1, numVal+1)
    pivotMat = numpy.ndarray(pivotShape, dtype=numpy.float32)
    
    '''The output goal here is to iterate over each element in values and populate a row in the variance matrix with the **drumroll** variance. 
    
    element[x] = square of the value - cumulative sum of the value * cumulative sum of the value / number of values.
    
    1. Lets try this just with numpy arrays to show what Serge has already shown - we can do this 'in' numpy.  This will be serial.
    
    2. Try the same approach, but instead load the value array into a shared memory array.  What are the prerequisites for doing that?
    
        2a. Each process needs access to the values for the entire values array.  Each process then writes to a specific column of the varMat.  We need to control which process writes to which line.  Luckily, the row.id = value.id, ie value[0] = row[0].  Each process only needs to know the index of the value and the value it is working with.
        
    3. Can we bail on these nested for loops?  Without testing - they have to be super slow.  I believe that vectorizing the math will be the fastest way.  The trick is going to be storing the cumulative values and incrementing the number of values.
    '''

    for i in range(1, numVal+1):
        '''With ever iteration, reset these constants, important later'''
        sumVals = 0
        sqVals = 0
        numVals = 0
        
        for j in xrange(i, numVal+1):
            val = float(values[j-1])
            sumVals += val 
            sqVals += val * val
            numVals += 1.0 #This is the n counter
            varMat[i][j] = sqVals - sumVals * sumVals / numVals #
            if i == 1:
                errorMat[j][1] = varMat[i][j]