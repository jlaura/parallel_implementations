from random import randint
import fj_serial_time
from mapclassify_time import PFisher_Jenks_MP
import fj_new_mp_time
import numpy

samples = [125,250,500,1000,2000,4000,8000,16000]
classes = [ 5, 7, 9]
for x in samples:
    for k in classes:
        values = [randint(0,5000) for y in range(0,x)]
        #values = ([120,108, 110, 108, 108, 108, 106, 108, 103, 103, 103, 104, 105, 102, 100, 99])
        
        times = fj_serial_time.fisher_jenks(values, k)
        print "FJ Serial using %i values and %i classes." %(x, k)
        print '=============================================================='
        print "Diameter Matrix Calculation: %f" %times[0]
        print "Error matrix Calculation: %f" %times[1]
        print "Find the Pivots: %f" %times[2]
        print "Total Time: %f" %times[3]
        print 
        
        times = PFisher_Jenks_MP(numpy.asarray(values))
        print "FJ Original multiprocessing using %i values and %i classes." %(x, k) 
        print '=============================================================='
        print "Diameter Matrix Calculation: %f" %times[0]
        print "Error matrix Calculation: %f" %times[1]
        print "Find the Pivots: %f" %times[2]
        print "Total Time: %f" %times[3]
        print 
        
        times = fj_new_mp_time.fisher_jenks(values, k)
        print "FJ Original multiprocessing using %i values and %i classes." %(x, k) 
        print '=============================================================='
        print "Diameter Matrix Calculation: %f" %times[0]
        print "Error matrix Calculation: %f" %times[1]
        print "Find the Pivots: %f" %times[2]
        print "Total Time: %f" %times[3]
        print 