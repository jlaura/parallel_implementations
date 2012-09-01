Parallel implementations of Fisher-Jenks optimal map classifier.
================================================================

Files
-----

 - `mp.py`: multiprocessing test
 - `pp.py`: parallel python test
 - `cl.py`: pyopencl test
 - `fisher_jenks.py`: sequential implementation of original algorithm

Dependencies
------------

 - pysal
 - pp
 - pyopencl


Install parallel python
-----------------------

    sudo easy_install pp

Install pyopencl
----------------

    git clone https://github.com/inducer/pyopencl.git
    cd pyopencl
    git submodule init
    git submodule update
    sudo make
    sudo make install


Notes
=====

If multiprocessing allows it, we could use dictionaries instead of numpy arrays to represent the Diameter (and Error) matrices since we only need the upper triangular elements and not the whole matrix. I added a second primitive class `fisher_jenks_d` to test this. It is slightly slower::


    In [2]: x = [12,10.8, 11, 10.8, 10.8, 10.8, 10.6, 10.8, 10.3, 10.3, 10.3, 10.4, 10.5, 10.2, 10.0, 9.9]

    In [3]: timeit fisher_jenks_d(x,5)
    100 loops, best of 3: 5.83 ms per loop

    In [4]: timeit fisher_jenks(x,5)
    100 loops, best of 3: 5.59 ms per loop

but it should have a smaller memory footprint than a full array.
