import mmap
import sys
import multiprocessing as mp
import time
t1 = time.time()
def g(lines):
    #time.sleep(10) - To show that we are using multiple threads.
    result = {}
    for x in range(0,len(lines),2):
        key = int(lines[x].split()[0])
        value = [int(neighbor) for neighbor in lines[x+1].split()]
        result[key] = value
    return result

#This version uses file
lines = open(sys.argv[1]).readlines()

#This version uses mmap
#lines = []
#with open(sys.argv[1], "r+b") as input_lines: #r+b is from the docs
    #m = mmap.mmap(input_lines.fileno(), 0, prot=mmap.PROT_READ)
    #for line in iter(input_lines.readline,""):
        #lines.append(line)

#This is consistant
n = int(lines[0:1][0])*2 # The *2 is GAL specific
numlines = 100000 #Has to be an even number for a GAL.
cores = mp.cpu_count() 
pool = mp.Pool(processes = cores)
lines = lines[1:] #Again GAL specific due to the header count
result_list = pool.map(g, (lines[line:line+numlines] for line in xrange(0,n*2,numlines)))

result = {}
map(result.update, result_list)
t2 = time.time()
print t2 - t1
#print result
#print "This should be the empty list. ", result[164]
#print "This is a sample.", result[195]


    
#with open(sys.argv[1], "r+b") as f:
    ##GAL Specific
    #filemap = mmap.mmap(f.fileno(), 0) #0 indicates read the whole thing - this needs to change for large files.
    #n = int(filemap.readline()) #We know that the first line is a header in a GAL file - a count of observations  
    ##print filemap.tell()  #By reading n we are set in the corret byte place.
    ##Get CPU count and start the pool of workers

    
    ##Setup an empty dict and use mp. to pack it with weights
    #w = {}
    #while True:
        #process = pool.map_async(g, [n, n-24])
        #if process:
            #w[process[0]] = process[1]
        #else:
            #break
    #print

    ##Can we seek to a line or only by byte? - Byte....dammit
    #print filemap.tell()
    #filemap.seek(10)
    #print filemap.tell()
    #print filemap.readline()
    
    
    #Sample how to get the line count using mmap - should be faster than looping and counting \n
    #filemap = mmap.mmap(f.fileno(), 0)
    #readline = filemap.readline
    #lines = 0
    #while readline():
        #lines += 1
    #print lines

    #Sample of how to read the integers from a line:
    #filemap = mmap.mmap(f.fileno(), 0)
    
    