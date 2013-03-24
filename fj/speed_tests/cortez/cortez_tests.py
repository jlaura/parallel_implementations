from random import randint
import fj_serial_time
from mapclassify_time import PFisher_Jenks_MP
import fj_refactored_sp
import fj_refactored_vect_only_sp
import numpy
import matplotlib.pyplot as plt

samples = [125,250,500,1000,2000,4000,8000,16000, 20000, 24000, 28000, 32000, 36000, 40000]
classes = [ 5 ]#, 7, 9]

for k in classes:
    fj_vec_only_diam=[]
    fj_new_mp_multi_diam = []

    fj_vec_only_err=[]
    fj_new_mp_multi_err = []

    fj_vec_only_piv=[]
    fj_new_mp_multi_piv = []
    
    fj_vec_only_total=[]
    fj_new_mp_multi_total = [] 

    for t in samples:
        values = [randint(0,5000) for y in range(0,t)]
        #values = ([120,108, 110, 108, 108, 108, 106, 108, 103, 103, 103, 104, 105, 102, 100, 99])
        
        times = fj_refactored_vect_only_sp.fisher_jenks(values, k)
        print "FJ Vectorized using %i values and %i classes." %(t, k) 
        print '=============================================================='
        print "Diameter Matrix Calculation: %f" %times[0]
        fj_vec_only_diam.append(times[0])
        print "Error matrix Calculation: %f" %times[1]
        fj_vec_only_err.append(times[1])
        print "Find the Pivots: %f" %times[2]
        fj_vec_only_piv.append(times[2])
        print "Total Time: %f" %times[3]
        fj_vec_only_total.append(times[3])
        print 
        
        times = fj_refactored_sp.fisher_jenks(values,k)
        print "FJ vectorized only using %i values and %i classes." %(t, k)
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
        
    fig = plt.figure(figsize=(10,10), dpi=300)
    
    
    #Plot the diameter matrix generation.
    a = fig.add_subplot(2,2,1)
    a.plot(samples, fj_vec_only_diam, c='orange', label='Vectorized', linewidth=1.5)
    a.plot(samples, fj_new_mp_multi_diam, c='green', label='Vectorized & Mp', linewidth=1.5)
    a.legend(loc='upper left')
    a.set_ylabel('time(s)')
    a.set_xlabel('# samples')
    a.set_title('Diameter Matrix Computation Time')
    #plt.show()
    #name = 'FINAL_DiameterMatrix_%i_classes.png' %k
    #plt.savefig(name, dpi=300)
    #plt.clf() #Clear this plot.
    
    
    #Plot the error matrix generation
    a = fig.add_subplot(2,2,2)
    a.plot(samples, fj_vec_only_err, c='orange', label='Vectorized', linewidth=1.5)
    a.plot(samples,fj_new_mp_multi_err, c='green', label='Vectorized & Mp', linewidth=1.5)
    a.legend(loc='upper left')
    a.set_ylabel('time(s)')
    a.set_xlabel('# samples')
    a.set_title('Error Matrix Computation Time')
    #plt.show()
    #name = 'FINAL_ErrorMatrix_%i_classes.png' %k
    #plt.savefig(name, dpi=300) 
    #plt.clf() #Clear this plot.
    
    #Plot the Pivot Matrix times
    a = fig.add_subplot(2,2,3)
    a.plot(samples, fj_vec_only_piv, c='orange', label='Vectorized', linewidth=1.5)
    a.plot(samples, fj_new_mp_multi_piv, c='green', label='Vectorized & Mp', linewidth=1.5)
    a.legend(loc='upper left')
    a.set_ylabel('time(s)')
    a.set_xlabel('# samples')
    a.set_title('Pivot Matrix Computation Time')
    #plt.show()
    #name = 'FINAL_PivotMatrix_%i_classes.png' %k
    #plt.savefig(name, dpi=300)
    #plt.clf() #Clear this plot.
    
    #Plot total time
    a = fig.add_subplot(2,2,4)
    a.plot(samples, fj_vec_only_total, c='orange', label='Vectorized', linewidth=1.5)
    a.plot(samples,fj_new_mp_multi_total, c='green', label='Vectorized & Mp', linewidth=1.5)
    a.legend(loc='upper left')
    a.set_ylabel('time(s)')
    a.set_xlabel('# samples')
    a.set_title('Total Computation Time')
    #plt.show()
    #name = 'FINAL_TotalTime_%i_classes.png' %k
    #plt.savefig(name, dpi=300)  
    #plt.clf() #Clear this plot. 
    fig.tight_layout()
    a.autoscale_view()
    fig.savefig('Cortez_Test.png')
    #plt.show()