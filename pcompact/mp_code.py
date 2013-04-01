import multiprocessing as mp
import pcompact_region as pc
import numpy as np
import random
import sys

#Testing
import os
import matplotlib
matplotlib.use("Agg")
import time
from math import sqrt
from pylab import imsave
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
cmap = ListedColormap(['red', 'green', 'blue', 'black', 'yellow', 'snow','peru','lightsalmon','gray','darkgreen'], 'indexed')

#This will use all cores, we can use any integer < max(cores). 
cores = mp.cpu_count() 

#Variables
if len(sys.argv) < 3:
    print "The script requires a .dbf file whose name begins with the number of elements in a row."
    print "The script also requires that you supply an integer number of IFS to generate."
    exit(0)
elif sys.argv[1].split(".")[1] != 'dbf':
    print "This script must target the shapefile dbf."
    exit(0)
    
inputds = sys.argv[1]
n = int(os.path.basename(sys.argv[1]).split("x")[0]) ** 2
p = int(sys.argv[2])
soln_space_size = 7
if p == 4:
    dealing_int = range(4,250)
    seed = [51,59,195,204]
if p == 16:
    dealing_int = range(16,250)
    seed = [17, 22, 26, 30, 81, 85, 90, 94, 162, 165, 170, 174, 225, 229, 234, 238]
if p ==64:
    dealing_int = range(64,250)
    seed = [ 0,  2,  4,  6,  8, 10, 12, 14, 32, 34, 36, 38, 40, 42, 44, 46,64, 66, 68, 70, 72, 74, 76,78, \
             96,  98, 100, 102, 104, 106, 108, 110,128, 130, 132, 134, 136, 138, 140, 142,160, 162, 164, 166, \
             168, 170, 172, 174,192, 194, 196, 198, 200, 202, 204, 206,224, 226, 228, 230, 232, 234, 236, 238 ]

def checkConnectivity(i, MZi, ZState, M):
    # if moving i from MZi will cause disconnected TAZ blocks, then no action is taken for this TAZ
    # ajacent TAZs
    ajTAZsofi = []
    if len(ZState[MZi])<=2:#
        return 0
    startTAZ = ZState[MZi][0]
    while True: #randomly choose a TAZ in this MZ to start with
        index = random.randint(0,len(ZState[MZi])-1)
        #print "index: ", index, " MZi: ", MZi, " len:", len(self.Zstate[MZi])
        startTAZ = ZState[MZi][index]
        if startTAZ != i:
            break
    #diffusing algorithm
    packOfTAZ = [startTAZ]
    j = 0
    flag = True
    while flag:
        for taz in M[packOfTAZ[j]]: #get all the neighbours of each TAZ in the MZ
            if (not (taz in packOfTAZ)) and (taz in ZState[MZi]) and (taz != i):
                packOfTAZ.append(taz)
        j += 1
        if j == len(packOfTAZ):
            flag = False

    if len(packOfTAZ) == len(ZState[MZi])-1:
        return 0
    else:
        return -1 
    

def computeCompactness2(area, inertia):
    pi = 3.1415926
    return (area**2)/(2*pi*inertia)    

def distance(pointX, pointY):
    return sqrt((pointX[0]-pointY[0])**2+(pointX[1]-pointY[1])**2) 

def divide(shape1,shape2):
    area = shape1[1] - shape2[1]
    xg = (shape1[1]*shape1[2]-shape2[1]*shape2[2])/area
    yg = (shape1[1]*shape1[3]-shape2[1]*shape2[3])/area
    Ig = shape1[0] - shape2[0] - area*(distance([shape1[2],shape1[3]],[xg,yg])**2) - shape2[1]*(distance([shape2[2],shape2[3]],[shape1[2],shape1[3]])**2)
    return [Ig, area, xg, yg]    

def merge(shape1,shape2):
    area1 = abs(shape1[1])
    area2 = abs(shape2[1])
    area = shape1[1] + shape2[1]
    rshape = []
    if area1 != 0.0 and area2 != 0.0:
        xg = (area1*shape1[2]+area2*shape2[2])/area
        yg = (area1*shape1[3]+area2*shape2[3])/area
        Ig = shape1[0] + shape2[0] + area1*(distance([shape1[2],shape1[3]],[xg,yg])**2)+area2*(distance([shape2[2],shape2[3]],[xg,yg])**2)
        rshape = [Ig, area, xg, yg]
    elif area1 == 0.0:
        rshape = shape2
    elif area2 == 0.0:
        rshape = shape1
    else:
        rshape = [0.0,0.0,0.0,0.0]
    return rshape

def deltaObjCal( i, MZi, neigbrMZ, ZstateProperties, T):
    #------------------------------------------------------------------------------------------------------
    # step2: calculate the new area, perimeter (if isoperimetric), moment of inertia, centroidX, centroidY
    #    if removing TAZ i from TAZMZmship[i]
    #------------------------------------------------------------------------------------------------------
    areaOfMZi = ZstateProperties[MZi][1] - T[i][1]
    PropMZi = [0,0,0,0]
    tmpPropertyMZi = [0,0,0,0,0,0,[],0,0,0,0]

    pMZi = ZstateProperties[MZi]
    shape1 = [pMZi[3],pMZi[1],pMZi[4],pMZi[5]]
    shape2 = [T[i][3],T[i][1],T[i][4],T[i][5]]
    PropMZi = divide(shape1,shape2) #obtain the properties of MZ after removing the TAZ from MZi
    objComptness = computeCompactness2(areaOfMZi,PropMZi[0])
    tmpPropertyMZi[3]=PropMZi[0] # moment of inertia
    tmpPropertyMZi[4]=PropMZi[2] # centroidX
    tmpPropertyMZi[5]=PropMZi[3] # centroidY

    overallObjMZi = objComptness
    # deltaObjMZi is used to measure the change of Obj of MZi
    deltaObjMZi = overallObjMZi - ZstateProperties[MZi][0]

    tmpPropertyMZi[0]=overallObjMZi # overallObj
    tmpPropertyMZi[1]=areaOfMZi   # area
    tmpPropertyMZi[7]= 0
    tmpPropertyMZi[8]= 0
    tmpPropertyMZi[9]= i # to move which TAZ
    tmpPropertyMZi[10]= MZi # from which MZ

    # change of objective function
    delObj = 0
    graspparameter = [-99999999,[0,0,0,0,0,0,[],0,0,0,0],[0,0,0,0,0,0,[],0,0,0,0]] #change of compactness (should be smaller and negative; move TAZ to which MZ; common arcL by adding TAZ i to MZk)
    # 0: delta Obj
    # 1: the properties of new MZi
    # 2: the properties of new MZk
    for MZk in neigbrMZ:
        areaOfMZk = ZstateProperties[MZk][1] + T[i][1]
        PropMZk = [0,0,0,0]
        tmpPropertyMZk = [0,0,0,0,0,0,[],0,0,0,0]
        pMZk = ZstateProperties[MZk]
        shape1 = [pMZk[3],pMZk[1],pMZk[4],pMZk[5]]
        shape2 = [T[i][3],T[i][1],T[i][4],T[i][5]]
        PropMZk = merge(shape1,shape2) #obtain the properties of MZ after removing the TAZ from MZi
        objComptness = computeCompactness2(areaOfMZk,PropMZk[0])
        tmpPropertyMZk[3]=PropMZk[0] # moment of inertia
        tmpPropertyMZk[4]=PropMZk[2] # centroidX
        tmpPropertyMZk[5]=PropMZk[3] # centroidY
        # CT + Compactness
        overallObjMZk = objComptness
        # deltaObjMZi is used to measure the change of Obj of MZk
        deltaObjMZk = overallObjMZk - ZstateProperties[MZk][0]
        tmpPropertyMZk[0]=overallObjMZk # overallObj
        tmpPropertyMZk[1]=areaOfMZk   # area
        tmpPropertyMZk[9]= i # to move which TAZ
        tmpPropertyMZk[10]= MZk # to which MZ

        delObj = deltaObjMZi +  deltaObjMZk   # new Obj_ik- old Obj_ik

        if delObj > graspparameter[0]:
            graspparameter[0] = delObj
            graspparameter[1] = tmpPropertyMZi
            graspparameter[2] = tmpPropertyMZk

    return graspparameter

def localsearch(unitRegionMemship, ZState, ZstateProperties, T,M,p, rand):
    #print "start local search"
    #setup SA parameters
    T0SA = 1
    alphaSA = 0.998
    TfinalSA = 0.01
    #global OriAveCmpt
    roundN = 0
    arrindex = 0
    while T0SA>=TfinalSA: #condition of SA
        try:
            ranindex = rand.randint(0,len(T)-1)
            keys = T.keys()
            i = keys[ranindex]
            neigbrTAZi = M[i] # get all neighbouring TAZs of i
            neigbrMZ = [] # the IDs of all neighbouring TAZ that a TAZ can be moved to
            MZi = unitRegionMemship[i]
            for e in M[i]: # get all the possible regions that basic unit i could be moved to
                if unitRegionMemship[e] != MZi:
                    if not unitRegionMemship[e] in neigbrMZ:# e should not be in the same region,the zone is not added to neigbrMZ before,  
                        neigbrMZ.append(unitRegionMemship[e]) #put all the different MZ i's neighbour belongs to            
            if len(neigbrMZ)>0:
                if checkConnectivity(i, MZi, ZState, M)==0:
                    graspparameter = deltaObjCal(i, MZi, neigbrMZ, ZstateProperties, T)
                    delObj = graspparameter[0]
                    if delObj > 0:
                        MZk = graspparameter[2][10]
                        unitRegionMemship[i] =  MZk # step1
                        ZState[MZi].remove(i) #step2
                        ZState[MZk].append(i) #step3
                        #step4: update properties of MZi
                        ZstateProperties[MZi][0:6] = graspparameter[1][0:6]
                        ZstateProperties[MZk][0:6] = graspparameter[2][0:6]
                        #OriAveCmpt = OriAveCmpt + delObj/len(self.Zstate)
                        OriAveCmpt = sum([ZstateProperties[kk][0] for kk in range(p)])/p
                        roundN += 1
                    T0SA *= alphaSA # SA
        except StopIteration:
            break
        
    return unitRegionMemship, ZState, ZstateProperties

def initialization(tup):
    start = tup[0]; stop = tup[1]; n = tup[2]; p = tup[3]; inputds = tup[4]; seed = tup[5]; dealing_int = tup[6]
    local_soln = {}
    for x in range(start, stop):
        '''This function performs phase I of the algorithm'''
        pcompact = pc.pCompactRegions(n,p,inputds)
        pcompact.getSeeds_from_lattice(seed)        
        pcompact.dealing(dealing_int)
        pcompact.greedy()
        soln_specs = [pcompact.unitRegionMemship, pcompact.Zstate, pcompact.ZstateProperties, pcompact.T, pcompact.M]
        local_soln[x] = soln_specs
    return local_soln
    

def local_search_wrapper(i, local_soln, soln, p, step_size):
    stop = i+stepsize
    if stop > len(soln):
        stop = len(soln)
    for y in range(i, stop):
        unitRegionMemship = soln[y][0]
        ZState = soln[y][1]
        ZstateProperties = soln[y][2]
        T = soln[y][3] #We returned the class instance in the dict, so grab is back
        M = soln[y][4] 
        pid=mp.current_process()._identity[0]
        rand = random.Random(pid)
        #Initialize the local search and pack the results into a dict, as above
        urm, zs, zsp = localsearch(unitRegionMemship, ZState, ZstateProperties, T,M,p, rand)
        soln_specs = [urm, zs, zsp]
        local_soln[y] = soln_specs 

for deal in dealing_int:    
    print "Problem Size | number of regions | number of IFS | dealing integer"
    print "        ",n,"            ", p,"            ", soln_space_size,"               " ,deal
    t1 = time.time()
    
    pool = mp.Pool(cores)
    stepsize = soln_space_size / cores
    rem = soln_space_size % cores
    sections = []
    for x in xrange(0,soln_space_size-rem,stepsize):
        sections.append([x,x+stepsize, n,p,inputds,seed, deal])
    sections[-1][1] += rem
    result_pool = pool.map(initialization, iterable=sections)
    soln = {}
    map(soln.update, result_pool)  
    ##Multiprocessing phase I
    #jobs = [mp.Process(target=initialization,args=(i,stepsize,n,p,inputds,soln, seed, deal)) for i in range(0, soln_space_size, stepsize)]
    
    #for job in jobs:
        #job.start()
    #for job in jobs:
        #job.join()
    #print soln
    #exit()
    t2 = time.time()
    print "Initialization Time"
    print t2-t1
    #print "Completed phase I in {} seconds for {} solutions with {} elements".format(t2-t1, soln_space_size, n)
    #print "Starting to save the output IFS as PNG."
    initial_avg = []

    #Plot the output of the initial phase and save as a PNG
    initial_avg = np.empty(len(soln))
    for x in range(len(soln)):
        overallObj = 0.0
        for y in soln[x][2]:
            overallObj += y[0]
        OriAveCmpt = overallObj/p
        average = OriAveCmpt
        initial_avg[x] = average
    
    t3 = time.time()
    #Multiprocessing Phase II
    manager = mp.Manager()
    local_soln = manager.dict()
    step_size = len(soln) / cores
    jobs = [mp.Process(target=local_search_wrapper, args=(i, local_soln, soln, p, step_size)) for i in range(0,len(soln),step_size)]
    
    for job in jobs:
        job.start()
    for job in jobs:
        job.join()
    
    t4 = time.time()
    print "Local Search Time"
    print str(t4-t3)

    initial_arr = np.empty(len(local_soln))
    average_arr = np.empty(len(local_soln))
    print len(local_soln)
    for x in range(len(local_soln)):
        overallObj = 0.0
        for y in local_soln[x][2]:
            overallObj += y[0]
        OriAveCmpt = overallObj/p
        average = OriAveCmpt
        initial_arr[x] = initial_avg[x]
        average_arr[x] = average
    
    print "Initial | Final"  
    print initial_arr
    print average_arr
    print "Iteration Complete"
    exit()