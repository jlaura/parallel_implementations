Intro 
======

Here I am testing some basics - changing from list of list iteration into numpy arrays. 
The diameter calculation code is identical.

To try the tests locally use:

    $ python -m timeit -n 3 'import Test1_Numpy4Allocation' 'Test1_Numpy4Allocation._fisher_jenks()' 
    
    $ python -m timeit -n 3 'import Test1_Numpy4Allocation' 'Test1_Numpy4Allocation._jay_fj()'

where n is the number if iterations to test.

The tests are hard coded to randomly generate n=5000 values into an unsorted vector with
each iteration.  Therefore, total times are not indicative of true performance with real
values.  They are internally consistant and comparable.

Here the code is the same between functions, save _jat_fj uses numpy arrays as the dtype.
I wonder if the slow down is not a product of the fact that the numpy arrays are float and
the python lists are int.  We are allocating a lot less memory via python.

Also, the memory problem we chatted about on the phone.  Could that be because of the way
python blocks off contiguous memory for lists.  It might have available memory for the list
but not have sufficient contiguous available memory.  Just a thought.


Timing Samples
==============

Matrix
-------
$ python -m timeit -n 3 'import Test1_Numpy4Allocation' 'Test1_Numpy4Allocation._fisher_jenks()'
3 loops, best of 3: 17.2 sec per loop

Numpy
------
$ python -m timeit -n 3 'import Test1_Numpy4Allocation' 'Test1_Numpy4Allocation._jay_fj()'
3 loops, best of 3: 21.3 sec per loop

There you have it!