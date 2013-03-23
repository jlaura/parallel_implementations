import multiprocessing as mp
import pcompact_region as pc
import numpy as np

cores = mp.cpu_count() #This will use all cores, we can use any integer < max(cores).
pool = mp.Pool(processes = cores) #Make a pool of workers.

#P-Compact Variables
n = 100
p = 4

#Test Data

#Global Solution Space

#Multiprocessing phase I


pcompact = pc.pCompactRegions(n,p,"n100.dbf")
pcompact.getSeeds_from_lattice([11,17,81,87])
pcompact.dealing(19)
pcompact.greedy()
print pcompact.unitRegionMemship
print pcompact.Zstate
print pcompact.ZstateProperties