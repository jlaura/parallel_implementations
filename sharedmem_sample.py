import numpy
import sys
import multiprocessing
import ctypes
import time
import cProfile

_ctypes_to_numpy = {
    ctypes.c_char : numpy.int8,
    ctypes.c_wchar : numpy.int16,
    ctypes.c_byte : numpy.int8,
    ctypes.c_ubyte : numpy.uint8,
    ctypes.c_short : numpy.int16,
    ctypes.c_ushort : numpy.uint16,
    ctypes.c_int : numpy.int32,
    ctypes.c_uint : numpy.int32,
    ctypes.c_long : numpy.int32,
    ctypes.c_ulong : numpy.int32,
    ctypes.c_double : numpy.int64, #This is new for this test
    ctypes.c_float : numpy.float32,
    ctypes.c_double : numpy.float64
}


_numpy_to_ctypes = dict((value, key) for key, value in
                                _ctypes_to_numpy.iteritems())

class SharedMemArray(object):
    """ Wrapper around multiprocessing.Array to share an array accross
        processes.
        
        From: http://www.alexfb.com/cgi-bin/twiki/view/PtPhysics/WebHome
    """

    def __init__(self, array):
        """ Initialize a shared array from a numpy array.

            The data is copied.
        """
        self.data = ndarray_to_shmem(array)
        self.dtype = array.dtype
        self.shape = array.shape

    def __array__(self):
        """ Implement the array protocole.
        """
        array = shmem_as_ndarray(self.data, dtype=self.dtype)
        array.shape = self.shape
        return array
 
    def asarray(self):
        return self.__array__()
    
    
def shmem_as_ndarray(data, dtype=float):
    """ Given a multiprocessing.Array object, as created by
    ndarray_to_shmem, returns an ndarray view on the data.
    """
    dtype = numpy.dtype(dtype)
    size = data._wrapper.get_size()/dtype.itemsize
    arr = numpy.frombuffer(buffer=data, dtype=dtype, count=size)
    return arr


def ndarray_to_shmem(array):
    """ Converts a numpy.ndarray to a multiprocessing.Array object.
    
        The memory is copied, and the array is flattened.
    """
    arr = array.reshape((-1, ))
    data = multiprocessing.RawArray(_numpy_to_ctypes[array.dtype.type], 
                                        arr.size)
    ctypes.memmove(data, array.data[:], len(array.data))
    return data

def init(shared_arr_):
    global shared_arr
    shared_arr = shared_arr_
    
def f(shared_arr, i):
    # I have always worked in numpy land, so we need to get the shared slice back to numpy
    arr = shared_arr.asarray()
    arr[i] *= -1 #Just to show that we can read and write
    #time.sleep(3) #The above is trivial, we need to take some time to show spawned processes

def main():
    #define the size of the array if you want, or let it default to 3000
    try: 
        n = sys.argv(1)
    except:
        n = 3000
        
    #Fill the array with random integers
    numpyarray = numpy.random.randint(0, high=100, size=(n,n))
    
    #Array is int64 - causing stack trace on this machine
    numpyarray = numpyarray.view('int8')
    
    #Copy the numpy array to a ctypes array.
    ctypesarray = SharedMemArray(numpyarray)
    
    '''Initialize the array as a global, why?  - This is something I pickedup from a code example, it does not work without it, but why?
    This intorduces an issue where the program leaks memory if we do this in a for loop.
    So you have to manually clean shared_arr from globals() to free the memory.  I have not tested enough to know why.
    '''
    init(ctypesarray)
    
    cores = multiprocessing.cpu_count()
    cores *=2 #Hyperthreading
    
    step = n // cores
    jobs = []
    
    if step != 0:
        for i in range(0,n,step): #We assume a square array here, otherwise n should be the size of some axis.
            p = multiprocessing.Process(target=f, args=(shared_arr, slice(i, i+step)))
            jobs.append(p)
            
        for job in jobs:
            job.start()
            
        for job in jobs:
            job.join()
    #print numpyarray
    #print numpyarray*-1
    #print shared_arr.asarray()
    
    #I checked with prints, but the line below will raise an error if the arrays differ.
    #numpy.testing.assert_equal((numpyarray*-1), shared_arr.asarray(), 'The arrays differ.', verbose=True)

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()

