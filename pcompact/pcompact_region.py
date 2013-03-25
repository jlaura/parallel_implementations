import math
import csv
import numpy as N
from datetime import datetime
import random
import pysal
#import xlrd #Read XLS, get Array b and c
class pCompactRegions:
    totalDealGreedy = 0 #total number of basic unit to be assigned first
    upperlimit = 99999999999 # give a big integer
    NbestObj = 3 # for choosing the N-best choices for each MZ in the greedy phase
    p = 1 #Region
    n = 1 #Unit
    regionObj = [] #length is p, regionObj[i] is the objective of region i
    TakenZones = []
    M = {} # key: ID, value: list of IDs which are neighbors of key ID
    V = {} #
    values = []
    unitRegionMemship = {} #key: ID of basic unit, value: index of regions
    allUnits = [] #ID of all basic units
    T = {} # property of a single basic unit
        # 0: Obj
        # 1: area
        # 2: perimeter
        # 3: intertia
        # 4: CentroidX
        # 5: CentroidY
        # 6: propertyvalue to calculate dissimilarity
        # index by ID of basic unit

    Zstate = [] #lengh equals to p, Zstate[i] records ID of basic unit in region i
    ZstateProperties = [] # record for the *CURRENT* state of a region, what is the area and perimeter
        # 0: compactness: is the before zoneCN
        # 1: area
        # 2: perimeter
        # 3: intertia
        # 4: CentroidX
        # 5: CentroidY
        # 6: dissimilairty value
    def _init_(self):
        #print "initialization"
        pass
    #read dbf file using pysal
    def __init__(self, n, p, filename):
        #print "initialize n basic unit, p regions and contiguity/attribute data"
        self.p  = p
        self.n = n
        self.filename = filename
        for i in range(p):
            self.Zstate.append([]) # ID of basic units within region i
            self.ZstateProperties.append([])
        db = pysal.open(filename,'r')
        #row structure
        #ID, SARS, X, Adjacent
        for row in db:
            #dbf's structure: ID, SAR1, Uniform2, Adjacent. Touching
            self.M[int(row[0])] = [int(s) for s in row[3].split(',')] #column index 3 gives the list of basic units which are adjacent
            self.V[int(row[0])] = row[1] #column index 1 #value to compute dissimilarity
            self.values.append([row[1], int(row[0])])
            self.allUnits.append(int(row[0]))
            self.T[int(row[0])] = [float(i) for i in [row[5]**2/(2*3.1415926*row[9]), row[5],row[6],row[9],row[7],row[8]]]
    def getSeeds_from_lattice(self, seeds): # randomly select seeds to grow regions
        for i in range(len(seeds)):
            self.Zstate[i] = [seeds[i]]
            self.ZstateProperties[i] =  self.T[seeds[i]]
            self.unitRegionMemship[seeds[i]] = i
        self.TakenZones += seeds
        #print str(seeds)
    def dealing(self, totalDealGreedy):
        self.totalDealGreedy = totalDealGreedy
        try:
            dealgreedycount = 0
            # M records all the neighbour TAZs to each TAZ, len(M)=#(TAZ)
            while dealgreedycount < self.totalDealGreedy and len(self.TakenZones) < self.n:
                dealgreedycount += 1
                randomArr = range(len(self.Zstate))
                i = 0
                while len(randomArr) > 0 :
                    ranindex = random.randint(0,len(randomArr)-1)
                    i = randomArr[ranindex]
                    randomArr.remove(i)
                    try:
                    # determine whether the current neighbour recorded in greedyParameters[i] has been assigned by comparing to the globalGreedy
                        roundgreedyParameter = [-99999999, 0, 0, 0, 0, 0, 0, 0]
                        # if the candidate TAZ was assigned or the MZ is grown
                        for e in self.Zstate[i]: # for current element(in the order of growing sequence)
                            neighboursOfe = self.M[e]
                            for neighe in neighboursOfe:
                                if (not (neighe in self.TakenZones)) : # if this neighe is not taken
                                    #*************************************
                                    #**need to add code here, change of Objective!!! deltaObj***
                                    #compute new objective when adding neighe to current region i
                                    area = 0
                                    perimeter = 0
                                    inertia = 0.0
                                    x = 0.0
                                    y = 0.0
                                    A0 = self.ZstateProperties[i][1] #Area
                                    X0 = self.ZstateProperties[i][4]
                                    Y0 = self.ZstateProperties[i][5]
                                    inertia0 = self.ZstateProperties[i][3]
                                    Ti = self.T[neighe]
                                    A1 = Ti[1] #Area
                                    X1 = Ti[4]
                                    Y1 = Ti[5]
                                    inertia1 = Ti[3]
                                    area = A0 + A1
                                    x = (A0*X0+A1*X1)/area
                                    y = (A0*Y0+A1*Y1)/area
                                    inertia = inertia0 + inertia1 + ((X0-x)**2+(Y0-y)**2)*A0 + ((X1-x)**2+(Y1-y)**2)*A1
                                    overallObj = self.computeCompactness2(area, inertia)
                                    deltaObj = overallObj - self.ZstateProperties[i][0]
                                    #*************************************
                                    if deltaObj > roundgreedyParameter[0] -self.ZstateProperties[i][0] :
                                        roundgreedyParameter = [overallObj, area, perimeter, inertia, x, y, neighe]

                        self.Zstate[i].append(roundgreedyParameter[6])
                        self.TakenZones.append(roundgreedyParameter[6])
                        self.ZstateProperties[i] = roundgreedyParameter[0:6] + [0]
                        self.unitRegionMemship[roundgreedyParameter[6]] =i
                    except (RuntimeError, TypeError, NameError):
                        #print "error occurs!"
                        raise
        except StopIteration:
            print "Timeout"
        #print "finished dealing!"
    def computeCompactness2(self, area, inertia):
        pi = 3.1415926
        return (area**2)/(2*pi*inertia)
    def checkConnectivity(self, i, MZi):
        # if moving i from MZi will cause disconnected TAZ blocks, then no action is taken for this TAZ
        # ajacent TAZs
        ajTAZsofi = []
        if len(self.Zstate[MZi])<=2:#
            return 0
        startTAZ = self.Zstate[MZi][0]
        while True: #randomly choose a TAZ in this MZ to start with
            index = random.randint(0,len(self.Zstate[MZi])-1)
            #print "index: ", index, " MZi: ", MZi, " len:", len(self.Zstate[MZi])
            startTAZ = self.Zstate[MZi][index]
            if startTAZ != i:
                break
        #diffusing algorithm
        packOfTAZ = [startTAZ]
        j = 0
        flag = True
        while flag:
            for taz in self.M[packOfTAZ[j]]: #get all the neighbours of each TAZ in the MZ
                if (not (taz in packOfTAZ)) and (taz in self.Zstate[MZi]) and (taz != i):
                    packOfTAZ.append(taz)
            j += 1
            if j == len(packOfTAZ):
                flag = False

        if len(packOfTAZ) == len(self.Zstate[MZi])-1:
            return 0
        else:
            return -1
    def distance(self,pointX, pointY):
        return math.sqrt((pointX[0]-pointY[0])**2+(pointX[1]-pointY[1])**2)
    # DIVIDE function: remove one TAZ (shape2) from a MZ (shape1)
    # shape
    # 0: Moment of Inertia
    # 1: area
    # 2: Xg
    # 3: Yg
    def divide(self, shape1,shape2):
        area = shape1[1] - shape2[1]
        xg = (shape1[1]*shape1[2]-shape2[1]*shape2[2])/area
        yg = (shape1[1]*shape1[3]-shape2[1]*shape2[3])/area
        Ig = shape1[0] - shape2[0] - area*(self.distance([shape1[2],shape1[3]],[xg,yg])**2) - shape2[1]*(self.distance([shape2[2],shape2[3]],[shape1[2],shape1[3]])**2)
        return [Ig, area, xg, yg]
    def merge(self,shape1,shape2):
        area1 = abs(shape1[1])
        area2 = abs(shape2[1])
        area = shape1[1] + shape2[1]
        rshape = []
        if area1 != 0.0 and area2 != 0.0:
            xg = (area1*shape1[2]+area2*shape2[2])/area
            yg = (area1*shape1[3]+area2*shape2[3])/area
            Ig = shape1[0] + shape2[0] + area1*(self.distance([shape1[2],shape1[3]],[xg,yg])**2)+area2*(self.distance([shape2[2],shape2[3]],[xg,yg])**2)
            rshape = [Ig, area, xg, yg]
        elif area1 == 0.0:
            rshape = shape2
        elif area2 == 0.0:
            rshape = shape1
        else:
            rshape = [0.0,0.0,0.0,0.0]
        return rshape
    #calculate the obj changes of moving TAZ i from MZi to neighbrMZ
    def deltaObjCal(self, i, MZi, neigbrMZ):
        #------------------------------------------------------------------------------------------------------
        # step2: calculate the new area, perimeter (if isoperimetric), moment of inertia, centroidX, centroidY
        #    if removing TAZ i from TAZMZmship[i]
        #------------------------------------------------------------------------------------------------------
        areaOfMZi = self.ZstateProperties[MZi][1] - self.T[i][1]
        PropMZi = [0,0,0,0]
        tmpPropertyMZi = [0,0,0,0,0,0,[],0,0,0,0]

        pMZi = self.ZstateProperties[MZi]
        shape1 = [pMZi[3],pMZi[1],pMZi[4],pMZi[5]]
        shape2 = [self.T[i][3],self.T[i][1],self.T[i][4],self.T[i][5]]
        PropMZi = self.divide(shape1,shape2) #obtain the properties of MZ after removing the TAZ from MZi
        objComptness = self.computeCompactness2(areaOfMZi,PropMZi[0])
        tmpPropertyMZi[3]=PropMZi[0] # moment of inertia
        tmpPropertyMZi[4]=PropMZi[2] # centroidX
        tmpPropertyMZi[5]=PropMZi[3] # centroidY

        overallObjMZi = objComptness
        # deltaObjMZi is used to measure the change of Obj of MZi
        deltaObjMZi = overallObjMZi - self.ZstateProperties[MZi][0]

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
            areaOfMZk = self.ZstateProperties[MZk][1] + self.T[i][1]
            PropMZk = [0,0,0,0]
            tmpPropertyMZk = [0,0,0,0,0,0,[],0,0,0,0]
            pMZk = self.ZstateProperties[MZk]
            shape1 = [pMZk[3],pMZk[1],pMZk[4],pMZk[5]]
            shape2 = [self.T[i][3],self.T[i][1],self.T[i][4],self.T[i][5]]
            PropMZk = self.merge(shape1,shape2) #obtain the properties of MZ after removing the TAZ from MZi
            objComptness = self.computeCompactness2(areaOfMZk,PropMZk[0])
            tmpPropertyMZk[3]=PropMZk[0] # moment of inertia
            tmpPropertyMZk[4]=PropMZk[2] # centroidX
            tmpPropertyMZk[5]=PropMZk[3] # centroidY
            # CT + Compactness
            overallObjMZk = objComptness
            # deltaObjMZi is used to measure the change of Obj of MZk
            deltaObjMZk = overallObjMZk - self.ZstateProperties[MZk][0]
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
    def greedy(self):
        #print "start greedy"
        greedyParameters = [[-99999999, 0, 0, 0, 0, 0, 0]]*len(self.Zstate) #record for the *FUTURE* state of MZ, what is the area and perimeter
        globalgreedyParameter = [-99999999, 0, 0, 0, 0, 0, 0, 0] #Structure the same as greedyParameters, #7: index of regions namely index of Zstate
        try:
            # M records all the neighbour TAZs to each TAZ, len(M)=#(TAZ)
            while len(self.TakenZones) < self.n: # while there is still unit not assigned to some region

                for i in range(len(self.Zstate)):
                    try:
                        # determine whether the current neighbour recorded in greedyParameters[i] has been assigned by comparing to the globalGreedy
                        roundgreedyParameter = [[-99999999, 0, 0, 0, 0, 0, 0, 0]] * self.NbestObj
                        if greedyParameters[i][6] == globalgreedyParameter[6] or i==globalgreedyParameter[7]:
                            flag = 0
                            for e in self.Zstate[i]: # for current element(in the order of growing sequence)
                                neighboursOfe = self.M[e]
                                for neighe in neighboursOfe:
                                    if not (neighe in self.TakenZones):
                                        #*************************************
                                        #**need to add code here, change of Objective!!! deltaObj***
                                        #compute new objective when adding neighe to current region i
                                        area = 0
                                        perimeter = 0
                                        inertia = 0.0
                                        x = 0.0
                                        y = 0.0
                                        A0 = self.ZstateProperties[i][1] #Area
                                        X0 = self.ZstateProperties[i][4]
                                        Y0 = self.ZstateProperties[i][5]
                                        inertia0 = self.ZstateProperties[i][3]
                                        Ti = self.T[neighe]
                                        A1 = Ti[1] #Area
                                        X1 = Ti[4]
                                        Y1 = Ti[5]
                                        inertia1 = Ti[3]
                                        area = A0 + A1
                                        x = (A0*X0+A1*X1)/area
                                        y = (A0*Y0+A1*Y1)/area
                                        inertia = inertia0 + inertia1 + ((X0-x)**2+(Y0-y)**2)*A0 + ((X1-x)**2+(Y1-y)**2)*A1
                                        overallObj = self.computeCompactness2(area, inertia)
                                        deltaObj = overallObj - self.ZstateProperties[i][0]
                                        #*************************************
                                        flagx = True
                                        # if this plan does not exist
                                        for xxx in roundgreedyParameter:
                                            if xxx[0]==overallObj:
                                                flagx = False
                                                break
                                        if flagx:
                                            if flag < self.NbestObj:
                                                roundgreedyParameter[flag] = [overallObj, area, perimeter, inertia, x, y, neighe]
                                                flag += 1
                                            else:
                                                indext = roundgreedyParameter.index(min(roundgreedyParameter)) # get the index of the minimal objective in roundgreedyParameter
                                                if deltaObj > (roundgreedyParameter[indext][0] - self.ZstateProperties[i][0]):
                                                    roundgreedyParameter[indext] = [overallObj, area, perimeter, inertia, x, y, neighe]

                            greedyParameters[i] = roundgreedyParameter[random.randint(0,self.NbestObj-1)] # randomly pick one of the N best growing plans
                            if greedyParameters[i][0] < -999999:
                                for x in roundgreedyParameter:
                                    if x[0]> -999999:
                                        greedyParameters[i] = x


                    except (RuntimeError, TypeError, NameError):
                        print "error occurs!"
                        raise

                #after all best N zoning plan identified for p regions
                globalgreedyParameter = [-99999999, 0, 0, 0, 0, 0, 0, 0]
                # choose the one that brings the most increase in objective
                for i in range(len(self.Zstate)):
                    if greedyParameters[i][0]> -9999999 and (greedyParameters[i][0]-self.ZstateProperties[i][0])> (globalgreedyParameter[0]-self.ZstateProperties[globalgreedyParameter[7]][0]):
                        globalgreedyParameter = greedyParameters[i] + [i]
                self.Zstate[globalgreedyParameter[7]].append(globalgreedyParameter[6])
                self.ZstateProperties[globalgreedyParameter[7]] = globalgreedyParameter[0:6] + [0] # update the objective function based on the TAZ zones in the current zone
                self.TakenZones.append(globalgreedyParameter[6])# set the status of this zone to "taken"
                self.unitRegionMemship[globalgreedyParameter[6]] = globalgreedyParameter[7]
        except StopIteration:
            print "Timeout"




    def localsearch(self):
        print "start local search"
        #setup SA parameters
        T0SA = 1
        alphaSA = 0.998
        TfinalSA = 0.01
        global OriAveCmpt
        roundN = 0
        arrindex = 0
        while T0SA>=TfinalSA: #condition of SA
            try:
                ranindex = random.randint(0,len(self.T)-1)
                keys = self.T.keys()
                i = keys[ranindex]
                neigbrTAZi = self.M[i] # get all neighbouring TAZs of i
                neigbrMZ = [] # the IDs of all neighbouring TAZ that a TAZ can be moved to
                MZi = self.unitRegionMemship[i]
                for e in self.M[i]: # get all the possible regions that basic unit i could be moved to
                    if self.unitRegionMemship[e] != MZi and (not(self.unitRegionMemship[e] in neigbrMZ)):# e should not be in the same region,
                                                     # the zone is not added to neigbrMZ before,
                        neigbrMZ.append(self.unitRegionMemship[e]) #put all the different MZ i's neighbour belongs to
                if len(neigbrMZ)>0:
                    if self.checkConnectivity(i, MZi)==0:
                        graspparameter = self.deltaObjCal(i, MZi, neigbrMZ)
                        delObj = graspparameter[0]
                        if delObj > 0:
                            MZk = graspparameter[2][10]
                            self.unitRegionMemship[i] =  MZk # step1
                            self.Zstate[MZi].remove(i) #step2
                            self.Zstate[MZk].append(i) #step3
                            #step4: update properties of MZi
                            self.ZstateProperties[MZi][0:6] = graspparameter[1][0:6]
                            self.ZstateProperties[MZk][0:6] = graspparameter[2][0:6]
                            #OriAveCmpt = OriAveCmpt + delObj/len(self.Zstate)
                            OriAveCmpt = sum([self.ZstateProperties[kk][0] for kk in range(self.p)])/self.p
                            roundN += 1
                        T0SA = T0SA * alphaSA # SA
            except StopIteration:
                break

#n = 100
#p = 4
#preg = pCompactRegions(n,p,"n100.dbf")
#preg.getSeeds_from_lattice([11,17,81,87])
#preg.dealing(19)
#preg.greedy()


#overallObj = 0.0
#for x in preg.ZstateProperties:
    #overallObj += x[0]
#OriAveCmpt = overallObj/p
#average = OriAveCmpt
#print "The average compactness has increased from: ", average
#preg.localsearch()
#overallObj = 0
#for x in preg.ZstateProperties:
    #overallObj += x[0]
#average_new = overallObj/p

#print "The average compactness has increased from: ", average, " --> ", average_new