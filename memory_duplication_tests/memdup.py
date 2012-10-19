import numpy
import multiprocessing
import ctypes
import random
import time

def allocate(values, classes):
    numVal = len(values)
    
    varShape = (numVal,numVal)
    print 'Initializing RawArray in:'
    time.sleep(1)
    print '3'
    time.sleep(1)
    print '2'
    time.sleep(1)
    print '1'
    varMat = multiprocessing.RawArray(ctypes.c_double, numVal*numVal)
    print 'RawArray created'
    time.sleep(5)
    
    print 'Getting view....maybe?'
    x = numpy.frombuffer(varMat)
    time.sleep(5)
    
    print 'Altering shape of the view without a copy...maybe'
    x.shape = varShape
    print x
    time.sleep(5)
    print 'X initialized as a global'
    initX(x) #Initialize x as a global
    
    step = numVal // 4 #num cores on my macbook
    jobs = []
    for i in range(0, numVal, step):
        p = multiprocessing.Process(target=f, args=(sharedX, slice(i, i+step)))
        jobs.append(p)
        p.start()
        p.join()

    
    print sharedX
        
    
def f(sharedVar, i):
    sharedVar[i] += (1000*random.random())
    
def initX(x_):
    global sharedX
    sharedX = x_

values = [int(1000*random.random()) for i in xrange(10000)]
print 'Values generated in a list.  Dtype is int'
time.sleep(5)
allocate(values, 5)
'''
Here we create a non-locking array inmemory that is accessible via numpy.

x = multiprocessing.RawArray(ctypes.c_double, numpy.arange(20))
print numpy.frombuffer(x)
'''


