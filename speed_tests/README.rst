============
Speed Tests
============

These are the graphical results of the speed tests.  Text results show that pivot values are the same for all methods.

time_test_final.py runs just the newest test.  For this test the following were implemented::

    errorMat is in a sharedmem array and multi-processed
    sharedmem arrays are not duplicating memory:
    
.. note:: Non-duplicating sharedmem needs to be tested.  It is much more naive than the original implementation.  I think it should be fine, reading the documentation, but needs testing with real data.
    
.. image:: https://github.com/jlaura/sharedmem-arrays/raw/master/speed_tests/FINAL_TotalTime_5_classes.png

Total Processing Time, k=5, Serial, Original Multiprocessing, Re-factored Multiprocessing

.. image:: https://github.com/jlaura/sharedmem-arrays/raw/master/speed_tests/FINAL_TotalTime_7_classes.png

Total Processing Time, k=7, Serial, Original Multiprocessing, Re-factored Multiprocessing

.. image:: https://github.com/jlaura/sharedmem-arrays/raw/master/speed_tests/FINAL_TotalTime_9_classes.png

Total Processing Time, k=9, Serial, Original Multiprocessing, Re-factored Multiprocessing

==============================
Total Time Breakdown by step:
==============================
.. note:: I omit timing allocation as this step is outside the scope of the optimization of FJ.  Allocation, in profiling large n values, requires approximately 1 second as a high end, conservative estimate.
  
.. note:: I omit showing processing time to determine pivots as it is less than 0.05 seconds in all tests with n < 36000.

Diameter Matrix
----------------
.. image:: https://github.com/jlaura/sharedmem-arrays/raw/master/speed_tests/FINAL_DiameterMatrix_5_classes.png

.. image:: https://github.com/jlaura/sharedmem-arrays/raw/master/speed_tests/FINAL_DiameterMatrix_7_classes.png

.. image:: https://github.com/jlaura/sharedmem-arrays/raw/master/speed_tests/FINAL_DiameterMatrix_9_classes.png

The majority of the computation time is spent in numpy.amin() indicating that even vectorized and multiprocessed, we are finally hitting the limits of numpy's optimization, ie. we are theoretically at C speeds + numpy's overhead.

Error Matrix
-------------
.. image:: https://github.com/jlaura/sharedmem-arrays/raw/master/speed_tests/ErrorMatrix_5_classes.png

.. image:: https://github.com/jlaura/sharedmem-arrays/raw/master/speed_tests/ErrorMatrix_5_classes.png

.. image:: https://github.com/jlaura/sharedmem-arrays/raw/master/speed_tests/ErrorMatrix_5_classes.png

To illustrate the 'cost' of multiprocessing, this next image compares the vectorized calculation of the error matrix in serial and multicored.  Waiting of individual cores to finish comprises the majority of the multiprocessing overhead - not the spawning of the threads.

.. image:: https://github.com/jlaura/sharedmem-arrays/raw/master/speed_tests/Serial_v_Multi_Err.png

===============
Large n values
===============

Using Cortez I tested performance of the script for large n values.  I would sugget that FJ is no longer constrained by processing time, but by the amount of available memory to build the diameter matrix.  I was able to max out Cortez at n = 50,000 (beyond this the system became unresponsive and I had to kill the process manually - see below).

.. image:: https://github.com/jlaura/sharedmem-arrays/raw/master/speed_tests/corteztests/cortez1_5.png

.. image:: https://github.com/jlaura/sharedmem-arrays/raw/master/speed_tests/corteztests/cortez1_5.png_7.png

I believe that the large decrease in slope seen at 36,000 - 40,000 and at 40,000 to 50,000 is caused by reads / writes to virtual memory.  At those levels a non-posix machine would likely crash out of python.  A posix machine handles this better, but hangs as it makes innumerable reads / writes to virtual memory.

======
To-Do
======
1. Modify the File I/O to return the data type to FJ.  We are allocating at 32-bit right now and could increase n substantially if we could determine that the input was 8 or 16-bit data.

2. Rewrite the memory testing.  The built-in module resource and external module pympler did not provide consistant, repeatable, or expected results.  Neither handled numpy arrays or multiple threads gracefully.

3. Cleanup all the commenting and get doc-tests written.
