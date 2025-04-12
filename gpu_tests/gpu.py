import numpy as np
from numba import jit, cuda
from timeit import default_timer as timer

# normal function to run on cpu
def func(a):                                
    for i in range(10000000):
        a[i] += 1     

# function optimized to run on gpu 
@cuda.jit                         
def func2(a):
    idx = cuda.grid(1)
    if idx < a.size:
        a[idx] += 1

if __name__ == "__main__":
    n = 10000000                           
    a = np.ones(n, dtype=np.float64)
     
    start = timer()
    func(a)
    print("without GPU:", timer() - start)    
     
    a = np.ones(n, dtype=np.float64)  # Reset array to initial state
    start = timer()
    threads_per_block = 1024
    blocks_per_grid = (a.size + (threads_per_block - 1)) // threads_per_block
    func2[blocks_per_grid, threads_per_block](a)
    cuda.synchronize()  # Ensure all threads have finished
    print("with GPU:", timer() - start)