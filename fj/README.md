################################################################
Parallel implementations of Fisher-Jenks optimal map classifier.
################################################################


The file `mp.py` runs loops for different sample sizes and different number of 
classes for the Multiprocessing implementation of Fisher-Jenks. It imports 
from `mapclassify.py` which, in addition to Multiprocessing, also imports 
pyopencl and pp which also are required. Instructions for installing these are 
below.


Install parallel python::
=========================

    easy_install pp

Install pyopencl:
=================

    git clone https://github.com/inducer/pyopencl.git
    git submodule init
    git submodule update
    sudo make
    sudo make install
