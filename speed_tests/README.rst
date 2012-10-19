============
Speed Tests
============

These are the graphical results of the speed tests.  Text results show that pivot values are the same for all methods.

time_test2.py runs just the newest test.  For this test the following were implemented::

    errorMat is in a sharedmem array
    sharedmem arrays are not duplicating memory
    
    .. note:: Non-duplicating sharedmem needs to be tested.  It is much more naive than the original implementation.  I think it should be fine, reading the documentation, but needs testing with real data.
    
.. image:: https://github.com/jlaura/sharedmem-arrays/raw/master/speed_tests/TotalTime_5_classes.png

My implementations duplicate memory briefly as memmove() is called.

.. image:: https://github.com/jlaura/sharedmem-arrays/raw/master/speed_tests/TotalTime_highSample.png

This implementation does not make a in memory copy.  When n > 8000, cache thrashing occurs, I think.  This is with approximately 3.2GB of memory free on a 4GB machine.
     
Questions
---------

1. When we read from a file, can we determine the dtype from the data coming in?  - maybe with regex?

2. In allocation, does the dtpye have to be float for everything? - This goes hand in hand with 1.  If we do not have to exist in float, then n can obviously get a lot larger.

3. When segmenting what are the pro/cons of using a generator?  - I commented out a half-baked function that does the segmenting.  As a series of sub-questions:

    a. We use iterators by default - they are easy.
    b. When is a generator appropriate?
    c. What about using 'with closing'?
    d. How does a generator interact with a multiprocessing pool?

4. What is pickling?  This is a big deal, as variables need to be pickable to be passed to multiprocessing.
