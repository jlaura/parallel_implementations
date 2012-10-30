import numpy
import timeit
import time
import multiprocessing
import sharedmem_sample
import warnings

'''Questions:

posix.waitpid - I believe that this is not actually forking.wait(), but the calls that happen in another thread / process.  The most time is therefore currently spent multiprocessing - is that correct?
'''

#Suppress the divide by zero errors
warnings.filterwarnings('ignore', category=RuntimeWarning)

def allocate(values, classes):
    numClass = classes

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
    
    del varMat
    
    return pivotMat, numClass, errorMat
	
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
    
def fisher_jenks(values, classes=5, sort=True):
    
    if sort:
	#pass
	values.sort()
	
    numVal = len(values)

    #Allocate all necessary memory
    pivotMat, k, errorMat = allocate(values, classes)
    
    #Calculate the number of cores over which to multiprocess
    cores = multiprocessing.cpu_count()
    cores *= 2
    step = numVal // cores

    t0 = time.time()
    #Calculate the variance matrix
    jobs = []
    for i in range(0,len(values),step):
	p = multiprocessing.Process(target=fj, args=(sharedVar, slice(i, i+step), values, i))
	jobs.append(p)
	
    for job in jobs:
	job.start()
	
    del jobs[:] #Empty the jobs list
    t1 = time.time()
    
    #Calculate the error matrix
    errorMat[0] = sharedVar.asarray()[0]
    
    #Error Matrix Calculation
    row = 1
    for x in errorMat[1:]: #Get each row, save the first
	errRow = x[row:] #Work only on the indices which will hold valid values
	for y in range(0,len(errRow)): #Iterate through each index in errRow
	    #print errorMat[row-1][row-1:y+row] 
	    #print sharedVar.asarray()[:,y+row][row:y+row+1]
	    errRow[y] = numpy.amin(errorMat[row-1][row-1:y+row] + sharedVar.asarray()[:,y+row][row:y+row+1])
	row += 1 #Iterate the row counter to get valid slices

    t2 = time.time()
    
    #Calculate Pivots
    pivots = []
    j = k - 1
    col = numVal - 1
    
    while j > 0:
	ev = errorMat[j, col]
	pivot_search = True
	right = col
	
	while pivot_search:
	    left_error = errorMat[j-1, right-1]
	    right_error = sharedVar.asarray()[right, col]
	    if left_error + right_error == ev:
		pivots.insert(0, right)
		col = right -1
		pivot_search = False
	    right -= 1
	j -=1
    t3 = time.time()
	
    print "Pivots: ", pivots
    return (t1-t0, t2-t1, t3-t2, t3-t0)

if __name__ == '__main__':
    values = numpy.arange(4000)
    fisher_jenks(values)
    