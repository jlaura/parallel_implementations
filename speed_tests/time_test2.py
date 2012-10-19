import fj_vectorized_time_sharedMem
import numpy
import matplotlib.pyplot as plt
from random import randint

samples = [125,250,500,1000,2000,4000,8000]
classes = [ 5 ]

for k in classes:
    fj_new_mp_fromBuff_diam = []
    fj_new_mp_fromBuff_err = []
    fj_new_mp_fromBuff_piv = []
    fj_new_mp_fromBuff_total = []
    
    for t in samples:
        values = [randint(0,5000) for y in range(0,t)]
        
        times = fj_vectorized_time_sharedMem.fisher_jenks(values, k)
        print "FJ vectorized, sharedmem, no duplication - using %i values and %i classes." %(t, k) 
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
    plt.plot(fj_new_mp_fromBuff_diam, samples, c='orange', label='From Buffer Tests', linewidth=2.0)
    plt.legend(loc='lower right')
    plt.xlabel('time(s)')
    plt.ylabel('# samples')
    plt.title('Diameter Matrix Computation Time')
    #plt.show()
    name = 'DiameterMatrix_highSample.png'
    plt.savefig(name, dpi=300)
    plt.clf() #Clear this plot.
    
    
    #Plot the error matrix generation
    plt.plot(fj_new_mp_fromBuff_err, samples, c='orange', label='From Buffer Tests', linewidth=2.0)
    plt.legend(loc='lower right')
    plt.xlabel('time(s)')
    plt.ylabel('# samples')
    plt.title('Error Matrix Computation Time')
    #plt.show()
    name = 'ErrorMatrix_highSample.png'
    plt.savefig(name, dpi=300) 
    plt.clf() #Clear this plot.
    
    #Plot total time
    plt.plot(fj_new_mp_fromBuff_total, samples, c='orange', label='From Buffer Tests', linewidth=2.0)
    plt.legend(loc='lower right')
    plt.xlabel('time(s)')
    plt.ylabel('# samples')
    plt.title('Total Computation Time')
    #plt.show()
    name = 'TotalTime_highSample.png'
    plt.savefig(name, dpi=300)  
    plt.clf() #Clear this plot. 