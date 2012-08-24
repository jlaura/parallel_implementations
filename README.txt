 This project is a short example of what I have been able to get working using shared memory arrays for reading and writing numpy in a multiprocessing evironment.  This is multiprocessing using the python built-in module (import multiprocessing).

A 3 second delay is introduced in function 'f' to allow time to see that multiple processes are spawned.

Omitting the time delay, the majority of the execution time (3000x3000 int8 array) is spent on the assert statement (11 / 12 seconds).

The issue with this code is the memory footprint.  numpy.random.randint returns an int64 array, which is converted to int8.

So we are fast...but mem constrained.
python -m timeit -n 3 'import sharedmem_sample' 'sharedmem_sample.main()'
3 loops, best of 3: 617 msec per loop