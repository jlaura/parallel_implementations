import multiprocessing as mp
import pcompact_region as pc
import numpy as np
import random
import sys
import pysal

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
np.set_printoptions(precision=5,threshold='nan')

f = open('output_log.txt', 'a')

#This will use all cores, we can use any integer < max(cores). 
try:
    cores = int(sys.argv[3]) 
except:
    print "Failed to get cores argument"
    cores = mp.cpu_count()

#Variables
if len(sys.argv) < 3:
    print "The script requires a .dbf file whose name begins with the number of elements in a row."
    print "The script also requires that you supply an integer number of IFS to generate."
    exit(0)
elif sys.argv[1].split(".")[1] != 'dbf':
    print "This script must target the shapefile dbf."
    exit(0)

#So we only open the file once    
db = pysal.open(sys.argv[1], 'r')
M={}
V={}
values=[]
allUnits=[]
T={}
for row in db:
    #dbf's structure: ID, SAR1, Uniform2, Adjacent. Touching
    M[int(row[0])] = [int(s) for s in row[3].split(',')] #column index 3 gives the list of basic units which are adjacent
    V[int(row[0])] = row[1] #column index 1 #value to compute dissimilarity
    values.append([row[1], int(row[0])])
    allUnits.append(int(row[0]))
    T[int(row[0])] = [float(i) for i in [row[5]**2/(2*3.1415926*row[9]), row[5],row[6],row[9],row[7],row[8]]]

n = int(os.path.basename(sys.argv[1]).split("x")[0]) ** 2
p = int(sys.argv[2])
soln_space_size = 20
if n == 256: #16x16
    if p == 4:
        dealing_int = range(37, 62)
        seed = [34,44,172,178]
    if p == 16:
        dealing_int = range(4,15)
        seed = [0,4,8,12,64,68,72,76,128,132,136,140,192,196,200,204]
    if p ==64:
        dealing_int = range(2,4)
        seed = [ 0,2,4,6,8,10,12,14,32,34,36,38,40,42,44,46,64,66,68,70,72,74,76,78,96,98,100,102,104,106,108,110,128,130,132,134,136,138,140,142,160,162,164,166,168,170,172,174,192,194,196,198,200,202,204,206,224,226,228,230,232,234,236,238]

elif n == 324: #18x18:
    if p == 9:
        dealing_int = range(4,34)
        seed = [0, 9, 17, 144, 153, 161, 306, 315, 323]
    elif p == 36:
        dealing_int = range(3,9)
        seed = [19, 22, 25, 28, 31, 34, 73, 76,79,82,85,88,127,130,133,136,139,142,181,184,187,190,193,196,235,238,241,244,247,250,289,292,295,298,301,304]
    elif p == 81:
        dealing_int = 3
        seed = [0,2,4,6,8,10,12,14,16,36,38,40,42,44,46,48,50,52,72,74,76,78,80,82,84,86,88,108,110,112,114,116,118,120,122,124,144,146,148,150,152,154,156,158,160,180,182,184,186,188,190,192,194,196,216,218,220,222,224,226,228,230,232,252,254,256,258,260,262,264,266,268,288,290,292,294,296,298,300,302,304]
elif n == 196: #14x14:
    if p == 49:
        dealing_int = range(1,4)
        seed = [0,2,4,6,8,10,12,28,30,32,34,36,38,40,56,58,60,62,64,66,68,84,86,88,90,92,94,96,112,114,116,118,120,122,124,140,142,144,146,148,150,152,168,170,172,174,176,178,180]
elif n == 400: #20x20
    if p == 25:
        dealing_int = range(2,15)
        seed = [0,4,8,12,16,80,84,88,92,96,160,164,168,172,176,240,244,248,252,256,320,324,328,332,336]
    elif p == 100:
        dealing_int = range(1,4)
        seed = [0,2,4,6,8,10,12,14,16,18,40,42,44,46,48,50,52,54,56,58,80,82,84,86,88,90,92,94,96,98,120,122,124,126,128,130,132,134,136,138,160,162,164,166,168,170,172,174,176,178,200,202,204,206,208,210,212,214,216,218,240,242,244,246,248,250,252,254,256,258,280,282,284,286,288,290,292,294,296,298,320,322,324,326,328,330,332,334,336,338,360,362,364,366,368,370,372,374,376,378]
        
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

    return unitRegionMemship, ZState, ZstateProperties

def initialization(tup):
    start = tup[0]
    stop = tup[1]
    n = tup[2]
    p = tup[3]
    M = tup[4]
    V = tup[5]
    T = tup[6]
    values = tup[7]
    allUnits = tup[8]
    seed = tup[9]
    deal = tup[10]
    
    local_soln = {}
    for x in range(start, stop):
        '''This function performs phase I of the algorithm'''
        pcompact = pc.pCompactRegions(n,p,M,V,T,values,allUnits)
        pcompact.getSeeds_from_lattice(seed)        
        pcompact.dealing(deal)
        pcompact.greedy()
        soln_specs = [pcompact.unitRegionMemship, pcompact.Zstate, pcompact.ZstateProperties, pcompact.T, pcompact.M]
        del pcompact
        local_soln[x] = soln_specs    
    return local_soln
    

def local_search_wrapper(i, local_soln, soln, p, step_size):
    stop = i+stepsize
    if stop > len(soln):
        stop = len(soln)
    #pid = mp.current_process()._identity
    #counter = 0
    for y in range(i, stop):
        #counter += 1
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
    #print pid, counter




    
for deal in dealing_int: 
    try:
        f.write("\n")
        f.write("\nProblem Size | number of regions | number of IFS | dealing integer | Cores")
        f.write("\n{},{},{},{},{}".format(n,p, soln_space_size,deal, cores))
        t1 = time.time()
        pool = mp.Pool(cores)
        stepsize = soln_space_size / cores
        rem = soln_space_size % cores
        
    
        soln = []
        def ifs(local_soln):
            for s in local_soln.values():
                soln.append(s)    
        
        sections = []       
        for x in xrange(0,soln_space_size-rem,stepsize):
            sections.append([x,x+stepsize,n,p,M,V,T,values,allUnits,seed, deal])
        sections[-1][1] += rem
        for section in sections:
            pool.apply_async(func=initialization, args=(section,), callback = ifs)
        pool.close()
        pool.join()
        
        t2 = time.time()
        f.write("\ntinit_{}_{}_{} = {}".format(n,p,deal, t2-t1))
        #print "Completed phase I in {} seconds for {} solutions with {} elements".format(t2-t1, soln_space_size, n)
        #print "Starting to save the output IFS as PNG."
        initial_avg = []
        #Plot the output of the initial phase and save as a PNG
        initial_avg = np.empty(len(soln))
        for x in range(len(soln)):
            #fig = plt.figure()
            #ax = fig.add_subplot(111)
            #axis_size =  int(sqrt(len(soln[x][0])))
            #Reshape the flat unit membership into a lattice and save.
            #local_img = []
            #for row in soln[x][0].itervalues(): 
                #local_img.append(row) 
            #local_img = np.asarray(local_img)
            #local_img.shape = (sqrt(len(soln[x][0])),sqrt(len(soln[x][0])))
            #plt.imshow(local_img, cmap=cmap, interpolation='none', extent=(0,axis_size,0,axis_size))
            overallObj = 0.0
            for y in soln[x][2]:
                #print y
                overallObj += y[0]
            OriAveCmpt = overallObj/p
            average = OriAveCmpt
            initial_avg[x] = average
            #initial_avg.append(average)
            #plt.title("The average compactness of solution {} \nis {}".format(x, average), fontsize=10)
            #ax.get_xaxis().set_ticks(range(axis_size))
            #ax.get_yaxis().set_ticks(range(axis_size))
            
            #plt.grid()
            #plt.savefig('Soln_' + str(x) + '_PhaseI.png', dpi=72)
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
        f.write("\ntlocal_{}_{}_{} = {}".format(n,p,deal, t4-t3))
    
        initial_arr = np.empty(len(local_soln))
        average_arr = np.empty(len(local_soln))
    
        for x in range(len(local_soln)):
            overallObj = 0.0
            for y in local_soln[x][2]:
                overallObj += y[0]
            OriAveCmpt = overallObj/p
            average = OriAveCmpt
            initial_arr[x] = initial_avg[x]
            average_arr[x] = average
        f.write("\ninit_{}_{}_{} = np.as{}".format(n,p,deal,np.array_repr(initial_arr, max_line_width=np.nan)))
        f.write("\nfinal_{}_{}_{} = np.as{}".format(n,p,deal,np.array_repr(average_arr, max_line_width=np.nan)))
        del manager, local_soln, jobs
    except:
        f.write("\n{},{},{},{},{} FAILED".format(n,p, soln_space_size,deal, cores))
        print "FAILED: {} {} {}".format(n,p,deal)
db.close()
f.close()