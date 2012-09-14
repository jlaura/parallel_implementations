Timeit:

values = numpy.arange(5000)

Serial:
python -m timeit -n 3 'import Test1_Numpy4Allocation' 'Test1_Numpy4Allocation._fisher_jenks()'
3 loops, best of 3: 12.4 sec per loop

Using ~500MB RAM

My Multiprocessing:
python -m timeit -n 3 'import Variance_Algorithm' 'Variance_Algorithm.main()'
3 loops, best of 3: 1.49 sec per loop

Spiking to ~800MB of RAM briefly.  That is the memmove.  It likely spiked to 1GB, but not long enough for Activity Monitor to catch it.


Variance Algorithm
------------------
I added the script Variance Algorithm where I ran through the way in which I think (thought) that variance should be calculated.  What am I doing wrong?

Lines 88 - 143 are a big block comment with the logic, plus the first few calculated by hand to prove(ish) that the algorithm is doing what I intended it 
to do.  Not that that means the algorithm is right...

Old
----
 This project is a short example of what I have been able to get working using shared memory arrays for reading and writing numpy in a multiprocessing evironment.  This is multiprocessing using the python built-in module (import multiprocessing).

A 3 second delay is introduced in function 'f' to allow time to see that multiple processes are spawned.

Omitting the time delay, the majority of the execution time (3000x3000 int8 array) is spent on the assert statement (11 / 12 seconds).

The issue with this code is the memory footprint.  numpy.random.randint returns an int64 array, which is converted to int8.
We then memmove the array - so we make a copy.  The goal would be to unwrap a numpy array (which is just a wrapper on a ctpyes array) and avoid the copy.

So we are fast...but mem constrained.
python -m timeit -n 3 'import sharedmem_sample' 'sharedmem_sample.main()'
3 loops, best of 3: 617 msec per loop
