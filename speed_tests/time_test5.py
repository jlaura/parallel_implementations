from random import randint
import fj_vectorized_time_sharedMem
import fj_vectorized_time_multi_err
import numpy
import matplotlib
matplotlib.use('Agg') #This allows MPL to plot with an active X session.
import matplotlib.pyplot as plt
import sys

name = sys.argv[1]
mem_name = sys.argv[2]
samples = [125,250,500,1000,2000,4000,6000]#,8000,16000, 24000, 32000, 36000, 40000]
classes = [ 5 ]#, 7, 9]

for k in classes:
    fj_new_mp_fromBuff_diam = []
    fj_new_mp_fromBuff_err = []
    fj_new_mp_fromBuff_piv = []
    fj_new_mp_fromBuff_total = []
    fj_new_mp_fromBuff_mem = []
    
    fj_new_mp_multi_diam = []
    fj_new_mp_multi_err = []
    fj_new_mp_multi_piv = []
    fj_new_mp_multi_total = []
    fj_new_mp_multi_mem = []    

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
        fj_new_mp_fromBuff_mem.append(times[4])
        
        times = fj_vectorized_time_multi_err.fisher_jenks(values,k)
        print "FJ all multiprocessed and from buffer using %i values and %i classes." %(t, k)
        print '=============================================================='
        print "Diameter Matrix Calculation: %f" %times[0]
        fj_new_mp_multi_diam.append(times[0])
        print "Error matrix Calculation: %f" %times[1]
        fj_new_mp_multi_err.append(times[1])
        print "Find the Pivots: %f" %times[2]
        fj_new_mp_multi_piv.append(times[2])
        print "Total Time: %f" %times[3]
        fj_new_mp_multi_total.append(times[3])
        print
        fj_new_mp_multi_mem.append((times[4]/1048576)) #B to MB, I think...

    #Plot the diameter matrix generation.
    plt.plot(fj_new_mp_fromBuff_err, samples,c='green', label='Serial Error Matrix Computation Time', linewidth=2.0, linestyle='--')
    plt.plot(fj_new_mp_fromBuff_total, samples, c='green', label='Serial Total Computation Time', linewidth=2.0)

    plt.plot(fj_new_mp_multi_err, samples, c='red', label='MP Error Matrix Computation Time', linewidth=2.0, linestyle='--')
    plt.plot(fj_new_mp_multi_total, samples, c='red', label='MP Total Computation Time', linewidth=2.0)
    
    plt.legend(loc='lower right')
    plt.xlabel('time(s)')
    plt.ylabel('# samples')
    plt.title('Serial vs. Multiprocessed Error Matrix Computation')
    plt.grid()
    #plt.show()
    name = '%s_%s.png' %(name, k)
    plt.savefig(name, dpi=300)
    plt.close()
    
    plt.plot(fj_new_mp_multi_mem, samples, c='red', label='Memory Usage', linewidth=2.0 )
    plt.legend(loc='lower right')
    plt.xlabel('RAM (MB)')
    plt.ylabel('# samples')
    plt.title('Total memory usage as measured by resource')
    plt.grid()
    plot_name = '%s_%s.png' %(mem_name, k)
    plt.savefig(plot_name, dpi=300)
    plt.close()
    