from random import randint
import fj_serial_time
from mapclassify_time import PFisher_Jenks_MP
import fj_new_mp_time #Non-vectorized errorMat calculation
import fj_new_mp_time_errMatTests #Vectorized errorMat calculation
import fj_vectorized_time_sharedMem
import numpy
import matplotlib.pyplot as plt

samples = [125,250,500,1000,2000,4000]#,8000,16000]
classes = [ 5 , 7, 9]

for k in classes:
    fj_serial_time_diam = []
    fj_pfisher_mp_diam = []
    fj_new_mp_diam = []
    fj_new_mp_errMatTests_diam = []
    fj_new_mp_fromBuff_diam = []

    fj_serial_time_err = []
    fj_pfisher_mp_err = []
    fj_new_mp_err = []
    fj_new_mp_errMatTests_err = []
    fj_new_mp_fromBuff_err = []

    fj_serial_time_piv = []
    fj_pfisher_mp_piv = []
    fj_new_mp_piv = []
    fj_new_mp_errMatTests_piv = []
    fj_new_mp_fromBuff_piv = []
    
    fj_serial_time_total = []
    fj_pfisher_mp_total = []
    fj_new_mp_total = []
    fj_new_mp_errMatTests_total = []
    fj_new_mp_fromBuff_total = []

    for t in samples:
        values = [randint(0,5000) for y in range(0,t)]
        #values = ([120,108, 110, 108, 108, 108, 106, 108, 103, 103, 103, 104, 105, 102, 100, 99])
        
        times = fj_serial_time.fisher_jenks(values, k)
        print "FJ Serial using %i values and %i classes." %(t, k)
        print '=============================================================='
        print "Diameter Matrix Calculation: %f" %times[0]
        fj_serial_time_diam.append(times[0])
        print "Error matrix Calculation: %f" %times[1]
        fj_serial_time_err.append(times[1])
        print "Find the Pivots: %f" %times[2]
        fj_serial_time_piv.append(times[2])
        print "Total Time: %f" %times[3]
        fj_serial_time_total.append(times[3])
        print 
        
        fj = PFisher_Jenks_MP(numpy.asarray(values), k)
        times = fj.time
        print "FJ Original multiprocessing using %i values and %i classes." %(t, k) 
        print '=============================================================='
        print "Diameter Matrix Calculation: %f" %times[0]
        fj_pfisher_mp_diam.append(times[0])
        print "Error matrix Calculation: %f" %times[1]
        fj_pfisher_mp_err.append(times[1])
        print "Find the Pivots: %f" %times[2]
        fj_pfisher_mp_piv.append(times[2])
        print "Total Time: %f" %times[3]
        fj_pfisher_mp_total.append(times[3])
        print 
        
        times = fj_new_mp_time.fisher_jenks(values, k)
        print "FJ new multiprocessing using %i values and %i classes." %(t, k) 
        print '=============================================================='
        print "Diameter Matrix Calculation: %f" %times[0]
        fj_new_mp_diam.append(times[0])
        print "Error matrix Calculation: %f" %times[1]
        fj_new_mp_err.append(times[1])
        print "Find the Pivots: %f" %times[2]
        fj_new_mp_piv.append(times[2])
        print "Total Time: %f" %times[3]
        fj_new_mp_total.append(times[3])
        print 
        
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
    plt.plot(fj_serial_time_diam ,samples, color='red', label='Serial', linewidth=2.0)
    plt.plot(fj_new_mp_diam, samples, c='green', label="Jay's Mp", linewidth=2.0)
    plt.plot(fj_pfisher_mp_diam, samples, c='blue', label='Original Mp', linewidth=2.0)
    plt.plot(fj_new_mp_errMatTests_diam, samples, c='yellow', label='Vectorized ErrorMat', linewidth=2.0)
    plt.plot(fj_new_mp_fromBuff_diam, samples, c='orange', label='From Buffer Tests', linewidth=2.0)
    plt.legend(loc='lower right')
    plt.xlabel('time(s)')
    plt.ylabel('# samples')
    plt.title('Diameter Matrix Computation Time')
    #plt.show()
    name = 'DiameterMatrix_%i_classes.png' %k
    plt.savefig(name, dpi=300)
    plt.clf() #Clear this plot.
    
    
    #Plot the error matrix generation
    plt.plot(fj_serial_time_err ,samples, color='red', label='Serial', linewidth=2.0)
    plt.plot(fj_new_mp_err, samples, c='green', label="Jay's Mp", linewidth=2.0)
    plt.plot(fj_pfisher_mp_err, samples, c='blue', label='Original Mp', linewidth=2.0)
    plt.plot(fj_new_mp_errMatTests_err, samples, c='yellow', label='Vectorized ErrorMat', linewidth=2.0)
    plt.plot(fj_new_mp_fromBuff_err, samples, c='orange', label='From Buffer Tests', linewidth=2.0)
    plt.legend(loc='lower right')
    plt.xlabel('time(s)')
    plt.ylabel('# samples')
    plt.title('Error Matrix Computation Time')
    #plt.show()
    name = 'ErrorMatrix_%i_classes.png' %k
    plt.savefig(name, dpi=300) 
    plt.clf() #Clear this plot.
    
    #Plot the Pivot Matrix times
    plt.plot(fj_serial_time_piv ,samples, color='red', label='Serial', linewidth=2.0)
    plt.plot(fj_new_mp_piv, samples, c='green', label="Jay's Mp", linewidth=2.0)
    plt.plot(fj_pfisher_mp_piv, samples, c='blue', label='Original Mp', linewidth=2.0)
    plt.plot(fj_new_mp_errMatTests_piv, samples, c='yellow', label='Vectorized ErrorMat', linewidth=2.0)
    plt.plot(fj_new_mp_fromBuff_piv, samples, c='orange', label='From Buffer Tests', linewidth=2.0)
    plt.legend(loc='lower right')
    plt.xlabel('time(s)')
    plt.ylabel('# samples')
    plt.title('Pivot Matrix Computation Time')
    #plt.show()
    name = 'PivotMatrix_%i_classes.png' %k
    plt.savefig(name, dpi=300)
    plt.clf() #Clear this plot.
    
    #Plot total time
    plt.plot(fj_serial_time_total ,samples, color='red', label='Serial', linewidth=2.0)
    plt.plot(fj_new_mp_total, samples, c='green', label="Jay's Mp", linewidth=2.0)
    plt.plot(fj_pfisher_mp_total, samples, c='blue', label='Original Mp', linewidth=2.0)
    plt.plot(fj_new_mp_errMatTests_total, samples, c='yellow', label='Vectorized ErrorMat', linewidth=2.0)
    plt.plot(fj_new_mp_fromBuff_total, samples, c='orange', label='From Buffer Tests', linewidth=2.0)
    plt.legend(loc='lower right')
    plt.xlabel('time(s)')
    plt.ylabel('# samples')
    plt.title('Total Computation Time')
    #plt.show()
    name = 'TotalTime_%i_classes.png' %k
    plt.savefig(name, dpi=300)  
    plt.clf() #Clear this plot.     