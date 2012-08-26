Parallel implementations of Fisher-Jenks optimal map classifier.
================================================================

Files
-----

 - `mp.py`: multiprocessing test
 - `pp.py`: parallel python test
 - `cl.py`: pyopencl test

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
