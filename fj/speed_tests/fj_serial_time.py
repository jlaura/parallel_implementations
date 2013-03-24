__author__  = "Sergio J. Rey <srey@asu.edu> "

import numpy as np
import time


__author__  = "Sergio J. Rey <srey@asu.edu> "

import numpy as np

def fisher_jenks(x, k):
    """
    Fisher-Jenks Optimal Partitioning of an ordered array into k classes

    Parameters
    ==========

    x: list of values to be partitioned
    k: number of classes to form

    Returns
    =======

    pivots: list (k-1) 
            since x order has to be respected, the first cluster begins 
            at element 0. The first value in pivots is the start of the second 
            class and the last value the start of the last class.

    Example
    =======
    >>> x = [12,10.8, 11, 10.8, 10.8, 10.8, 10.6, 10.8, 10.3, 10.3, 10.3, \
            10.4, 10.5, 10.2, 10.0, 9.9]
    >>> p2 = fisher_jenks(x,2)
    >>> p2
    [1]
    >>> p4 = fisher_jenks(x,4)
    >>> p4
    [1, 8, 14]
    >>> p5 = fisher_jenks(x,5)
    >>> p5
    [1, 6, 8, 14]

    """
    x.sort()
    x = np.array(x)
    # stage 1 diameter matrix
    n = len(x)
    Diameter = np.zeros((n,n),'float')
    Error  = np.zeros((k,n), 'float') #Moved to get it out of the timeing loop
    n_1 = n - 1
    
    t0 = time.time()
    for i in range(n_1):
        for j in range(i+1,n):
            Diameter[i,j] = x[i:j+1].var() * ( j - i + 1 )
    t1 = time.time()

    # stage 2 error matrix
    # find the optimal partition of  objects 0 through J into L clusters and store sum of 
    # cluster diameters in Error[L,J]
    
    Error[0] = Diameter[0]
    for row in range(1,k):
        for col in range(row+1,n):
            best = np.inf
            right = col
            while right >= row:
                rv = Diameter[right,col]
                e = Error[row-1,right-1]
                if  rv + e < best:
                    best = rv + e
                right -= 1
            Error[row,col] = best
    t2 = time.time()       

    # stage 3 finding pivots
    j = k - 1
    col = n_1
    pivots = []
    while j  > 0:
        ev = Error[j,col]
        pivot_search = True 
        right = col
        while pivot_search:
            left_error = Error[j-1, right-1]
            right_error = Diameter[right,col]
            if left_error + right_error == ev:
                pivots.insert(0,right)
                col = right - 1
                pivot_search = False
            right -= 1
        j -= 1
    t3 = time.time()    
    # pivots have the start ids for the second through last clusters
    #return pivots
    print "Pivots: ", pivots
    return (t1-t0, t2-t1, t3-t2, t3-t0)









