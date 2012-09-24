jay_fj.py
==========

This is currently working and returning the expected values.

The Good
---------
1. Calculation of the diameter matrix is completely vectorized.
2. The calculation of the error matrix is done in shared memory space
3. A pivot matrix is not allocated, it lives in a list.

The Bad
--------
1. This is really slow at the moment (140s when n=5000 and k=5) due to lots of waiting.  This is because of the naive split that is used in the calculation of the error matrix.  

The Plan
---------
I believe that I can use a modified binary search to calculate the ideal partitions without the need for additional memory.  This way it is possible to give each core the ideal number of calculations to balance processing time.