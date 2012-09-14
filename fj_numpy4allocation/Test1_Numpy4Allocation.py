'''These are the tests that I have started to run with the iterative conversion from pure python to numpy.'''

import numpy
import time
import timeit

def _fisher_jenks(classes=5, sort=True):
    values = numpy.arange(5000)

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
                
if __name__ == '__main__':
    _fisher_jenks()