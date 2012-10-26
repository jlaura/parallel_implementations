from random import randint
import fj_vectorized_time_sharedMem
import numpy
import matplotlib
matplotlib.use('Agg') #This allows MPL to plot with an active X session.
import matplotlib.pyplot as plt
import sys

name = sys.argv[1]
samples = [125,250]#],500,1000,2000,4000,8000,16000, 24000, 32000, 36000, 40000]
classes = [ 5 ]#, 7, 9]

for k in classes:
    fj_new_mp_fromBuff_diam = []
    fj_new_mp_fromBuff_err = []
    fj_new_mp_fromBuff_piv = []
    fj_new_mp_fromBuff_total = []

    for t in samples:
        values = [randint(0,5000) for y in range(0,t)]
        #values = ([120,108, 110, 108, 108, 108, 106, 108, 103, 103, 103, 104, 105, 102, 100, 99])


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
    plt.plot(fj_new_mp_fromBuff_diam, samples, c='red', label='Diameter Matrix Computation Time', linewidth=2.0)
    plt.plot(fj_new_mp_fromBuff_err, samples, c='blue', label='Error Matrix Computation Time', linewidth=2.0)
    plt.plot(fj_new_mp_fromBuff_total, samples, c='green', label='Total Computation Time', linewidth=2.0)
    plt.legend(loc='lower right')
    plt.xlabel('time(s)')
    plt.ylabel('# samples')
    plt.title('Large n Tests on Cortez')
    plt.grid()
    #plt.show()
    name = '%s.png' %name
    plt.savefig(name, dpi=300)