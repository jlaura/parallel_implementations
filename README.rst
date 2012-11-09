================
Parallelized FJ
================

This repository holds a newly parallelized implementation of the Fisher-Jenks algorithm.  Figure 1, below, shows the speed improvement over a serial implementation and the original multiprocessing implementation.  This new implementation also avoids creating in memory copies of arrays.
    
.. image:: https://github.com/jlaura/sharedmem-arrays/raw/master/speed_tests/Figure1.png

For all tests above k=5.  An increase in k impacts total processing time little.  See the speed_test directory for additional figures where k = {5,7,9}.

.. image:: https://github.com/jlaura/sharedmem-arrays/raw/master/speed_tests/Figure2.png

These figures show the potential overhead introduced by multiprocessing.  The majority of the speed increase is not due to parallelization, but vectorization using NumPy.

Large n values on a 12 core machine
------------------------------------
.. image:: https://github.com/jlaura/sharedmem-arrays/raw/master/speed_tests/Cortez_Test.png