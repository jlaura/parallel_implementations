from random import randint
import fj_serial_time
from mapclassify_time import PFisher_Jenks_MP
import fj_new_mp_time #Non-vectorized errorMat calculation
import fj_new_mp_time_errMatTests #Vectorized errorMat calculation
import fj_vectorized_time_sharedMem
import numpy
import matplotlib.pyplot as plt

samples = [125,250,500,1000,2000,4000,8000,16000]
classes = [ 5 , 7, 9]

for k in classes:
    fj_new_mp_errMatTests_diam = []
    fj_new_mp_fromBuff_diam = []

    fj_new_mp_errMatTests_err = []
    fj_new_mp_fromBuff_err = []

    fj_new_mp_errMatTests_piv = []
    fj_new_mp_fromBuff_piv = []

    fj_new_mp_errMatTests_total = []
    fj_new_mp_fromBuff_total = []

    for t in samples:
        values = [randint(0,5000) for y in range(0,t)]
        #values = ([120,108, 110, 108, 108, 108, 106, 108, 103, 103, 103, 104, 105, 102, 100, 99])
        
        times = fj_new_mp_time_errMatTests.fisher_jenks(values, k)
        print "FJ new with vectorized, single core, error matrix using %i values and %i classes." %(t, k) 
        print '=============================================================='
        print "Diameter Matrix Calculation: %f" %times[0]
        fj_new_mp_errMatTests_diam.append(times[0])
        print "Error matrix Calculation: %f" %times[1]
        fj_new_mp_errMatTests_err.append(times[1])
        print "Find the Pivots: %f" %times[2]
        fj_new_mp_errMatTests_piv.append(times[2])
        print "Total Time: %f" %times[3]
        fj_new_mp_errMatTests_total.append(times[3])
        print 
    
        times = fj_vectorized_time_sharedMem.fisher_jenks(values, k)
        print "FJ vectorized, single core, error matrix, numpy from buffer, using %i values and %i classes." %(t, k) 
        print '=============================================================='
        print "Diameter Matrix Calculation: %f" %times[0]
        fj_new_mp_fromBuff_diam.append(times[0])
        print "Error matrix Calculation: %f" %times[1]
        fj_new_mp_fromBuff_err.append(times[1])
        print "Find the Pivots: %f" %times[2]
        fj_new_mp_fromBuff_piv.append(times[2])
        print "Total Time: %f" %times[3]
        fj_new_mp_fromBuff_total.append(times[3])
        print 
        
    #Plot the diameter matrix generation.
    plt.plot(fj_new_mp_errMatTests_diam, samples, c='yellow', label='Vectorized ErrorMat', linewidth=2.0)
    plt.plot(fj_new_mp_fromBuff_diam, samples, c='orange', label='From Buffer Tests', linewidth=2.0)
    plt.legend(loc='lower right')
    plt.xlabel('time(s)')
    plt.ylabel('# samples')
    plt.title('Diameter Matrix Computation Time')
    #plt.show()
    name = 'DiameterMatrix_vect_spd.png' 
    plt.savefig(name, dpi=300)
    plt.clf() #Clear this plot.
    
    
    #Plot the error matrix generation
    plt.plot(fj_new_mp_errMatTests_err, samples, c='yellow', label='Vectorized ErrorMat', linewidth=2.0)
    plt.plot(fj_new_mp_fromBuff_err, samples, c='orange', label='From Buffer Tests', linewidth=2.0)
    plt.legend(loc='lower right')
    plt.xlabel('time(s)')
    plt.ylabel('# samples')
    plt.title('Error Matrix Computation Time')
    #plt.show()
    name = 'ErrorMatrix_vect_spd.png' 
    plt.savefig(name, dpi=300) 
    plt.clf() #Clear this plot.
    
    #Plot the Pivot Matrix times
    plt.plot(fj_new_mp_errMatTests_piv, samples, c='yellow', label='Vectorized ErrorMat', linewidth=2.0)
    plt.plot(fj_new_mp_fromBuff_piv, samples, c='orange', label='From Buffer Tests', linewidth=2.0)
    plt.legend(loc='lower right')
    plt.xlabel('time(s)')
    plt.ylabel('# samples')
    plt.title('Pivot Matrix Computation Time')
    #plt.show()
    name = 'PivotMatrix_vect_spd.png'
    plt.savefig(name, dpi=300)
    plt.clf() #Clear this plot.
    
    #Plot total time
    plt.plot(fj_new_mp_errMatTests_total, samples, c='yellow', label='Vectorized ErrorMat', linewidth=2.0)
    plt.plot(fj_new_mp_fromBuff_total, samples, c='orange', label='From Buffer Tests', linewidth=2.0)
    plt.legend(loc='lower right')
    plt.xlabel('time(s)')
    plt.ylabel('# samples')
    plt.title('Total Computation Time')
    #plt.show()
    name = 'TotalTime_vect_spd.png'
    plt.savefig(name, dpi=300)  
    plt.clf() #Clear this plot.     
