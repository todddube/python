import numpy as np
from numba import cuda, jit
import math
from timeit import default_timer as timer
import matplotlib.pyplot as plt
import concurrent.futures
import warnings

# Constants for optimization
TILE_SIZE = 16  # Tile size for matrix multiplication
MAX_TPB = 1024  # Maximum threads per block
WARMUP_RUNS = 3  # Number of warmup runs before benchmarking
TEST_RUNS = 5    # Number of test runs for averaging

# Additional constants for memory tests
KB = 1024
MB = 1024 * KB
GB = 1024 * MB

# CUDA kernel for optimized matrix multiplication using shared memory
@cuda.jit
def matrix_mul_shared_kernel(A, B, C):
    # Shared memory arrays for the current block
    tile_A = cuda.shared.array(shape=(TILE_SIZE, TILE_SIZE), dtype=np.float32)
    tile_B = cuda.shared.array(shape=(TILE_SIZE, TILE_SIZE), dtype=np.float32)
    
    row = cuda.blockIdx.x * TILE_SIZE + cuda.threadIdx.x
    col = cuda.blockIdx.y * TILE_SIZE + cuda.threadIdx.y
    tx = cuda.threadIdx.x
    ty = cuda.threadIdx.y
    
    tmp = 0
    # Loop over tiles
    for i in range((A.shape[1] + TILE_SIZE - 1) // TILE_SIZE):
        # Load data into shared memory
        x = row
        y = i * TILE_SIZE + ty
        if x < A.shape[0] and y < A.shape[1]:
            tile_A[tx, ty] = A[x, y]
        else:
            tile_A[tx, ty] = 0
            
        x = i * TILE_SIZE + tx
        y = col
        if x < B.shape[0] and y < B.shape[1]:
            tile_B[tx, ty] = B[x, y]
        else:
            tile_B[tx, ty] = 0
            
        cuda.syncthreads()
        
        # Compute partial dot product
        for j in range(TILE_SIZE):
            tmp += tile_A[tx, j] * tile_B[j, ty]
            
        cuda.syncthreads()
    
    if row < C.shape[0] and col < C.shape[1]:
        C[row, col] = tmp

# CUDA kernel for vector operations (more complex than simple addition)
@cuda.jit
def vector_ops_kernel(a, b, c, d):
    idx = cuda.grid(1)
    if idx < a.size:
        # More complex operation: d[i] = sin(a[i]) * cos(b[i]) + sqrt(abs(c[i]))
        d[idx] = math.sin(a[idx]) * math.cos(b[idx]) + math.sqrt(abs(c[idx]))

# CPU version of complex vector operations for comparison
def vector_ops_cpu(a, b, c):
    return np.sin(a) * np.cos(b) + np.sqrt(np.abs(c))

def benchmark_complex_vector_ops(size):
    """Benchmark complex vector operations on CPU and GPU"""
    # Generate random vectors
    a = np.random.random(size).astype(np.float32)
    b = np.random.random(size).astype(np.float32)
    c = np.random.random(size).astype(np.float32)
    d = np.zeros_like(a)
    
    # CPU benchmark
    start = timer()
    cpu_result = vector_ops_cpu(a, b, c)
    cpu_time = timer() - start
    
    # GPU benchmark
    threads_per_block = 256
    blocks_per_grid = (size + (threads_per_block - 1)) // threads_per_block
    
    # Copy data to device
    start = timer()
    d_a = cuda.to_device(a)
    d_b = cuda.to_device(b)
    d_c = cuda.to_device(c)
    d_d = cuda.to_device(d)
    
    # Run kernel
    vector_ops_kernel[blocks_per_grid, threads_per_block](d_a, d_b, d_c, d_d)
    cuda.synchronize()
    
    # Copy result back to host
    gpu_result = d_d.copy_to_host()
    gpu_time = timer() - start
    
    # Verify results
    np.testing.assert_allclose(cpu_result, gpu_result, rtol=1e-5, atol=1e-5)
    
    return cpu_time, gpu_time

def benchmark_matrix_multiplication_shared(size):
    """Benchmark matrix multiplication with shared memory on GPU"""
    # Generate random matrices
    A = np.random.random((size, size)).astype(np.float32)
    B = np.random.random((size, size)).astype(np.float32)
    C = np.zeros((size, size), dtype=np.float32)
    
    # CPU benchmark
    start = timer()
    cpu_result = np.dot(A, B)
    cpu_time = timer() - start
    
    # GPU benchmark
    threads_per_block = (TILE_SIZE, TILE_SIZE)
    blocks_per_grid = (
        math.ceil(A.shape[0] / TILE_SIZE), 
        math.ceil(B.shape[1] / TILE_SIZE)
    )
    
    start = timer()
    # Copy data to device
    d_A = cuda.to_device(A)
    d_B = cuda.to_device(B)
    d_C = cuda.to_device(C)
    
    # Run kernel
    matrix_mul_shared_kernel[blocks_per_grid, threads_per_block](d_A, d_B, d_C)
    cuda.synchronize()
    
    # Copy result back to host
    gpu_result = d_C.copy_to_host()
    gpu_time = timer() - start
    
    # Verify results
    np.testing.assert_allclose(cpu_result, gpu_result, rtol=1e-5, atol=1e-5)
    
    return cpu_time, gpu_time

@cuda.jit
def memory_bandwidth_kernel(src, dst):
    idx = cuda.grid(1)
    if idx < src.size:
        # Read and write operation to test memory bandwidth
        dst[idx] = src[idx] * 2.0

def benchmark_memory_bandwidth(size):
    """Benchmark memory transfer and bandwidth"""
    # Generate data
    src = np.random.random(size).astype(np.float32)
    dst = np.zeros_like(src)
    
    # CPU benchmark
    start = timer()
    dst_cpu = src * 2.0
    cpu_time = timer() - start
    
    # GPU benchmark
    threads_per_block = 256
    blocks_per_grid = (size + (threads_per_block - 1)) // threads_per_block
    
    start = timer()
    # Memory transfer to device
    d_src = cuda.to_device(src)
    d_dst = cuda.to_device(dst)
    
    # Run kernel
    memory_bandwidth_kernel[blocks_per_grid, threads_per_block](d_src, d_dst)
    cuda.synchronize()
    
    # Transfer result back
    gpu_result = d_dst.copy_to_host()
    gpu_time = timer() - start
    
    # Verify results
    np.testing.assert_allclose(dst_cpu, gpu_result, rtol=1e-5, atol=1e-5)
    
    return cpu_time, gpu_time

def benchmark_combined_stress(size):
    """Run multiple operations to stress the GPU"""
    # Generate data
    matrix_size = min(size, 4096)  # Limit matrix size for memory
    vector_size = size
    
    # Matrix multiplication
    cpu_time_mat, gpu_time_mat = benchmark_matrix_multiplication_shared(matrix_size)
    
    # Vector operations
    cpu_time_vec, gpu_time_vec = benchmark_complex_vector_ops(vector_size)
    
    # Memory bandwidth
    cpu_time_mem, gpu_time_mem = benchmark_memory_bandwidth(vector_size)
    
    # Combined time (parallel operations would be faster but this is for stress testing)
    cpu_time = cpu_time_mat + cpu_time_vec + cpu_time_mem
    gpu_time = gpu_time_mat + gpu_time_vec + gpu_time_mem
    
    return cpu_time, gpu_time

def plot_results(sizes, cpu_times, gpu_times, operation):
    """Plot comparison of CPU vs GPU performance"""
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, cpu_times, 'o-', label='CPU', color='blue')
    plt.plot(sizes, gpu_times, 'o-', label='GPU', color='red')
    plt.plot(sizes, [cpu_times[i]/gpu_times[i] for i in range(len(sizes))], 
             'g--', label='Speedup', alpha=0.5)
    plt.xlabel('Size')
    plt.ylabel('Time (seconds)')
    plt.title(f'CPU vs GPU Performance: {operation}')
    plt.legend()
    plt.grid(True)
    plt.yscale('log')
    plt.xscale('log')
    return plt

def print_gpu_info():
    """Print information about available CUDA devices"""
    if not cuda.is_available():
        print("❌ CUDA is not available!")
        return False
    
    print("✅ CUDA is available!")
    device = cuda.get_current_device()
    print(f"\nGPU Device: {device.name}")
    print(f"Compute Capability: {device.compute_capability}")
    print(f"Max threads per block: {device.MAX_THREADS_PER_BLOCK}")
    print(f"Max block dimensions: {device.MAX_BLOCK_DIM_X}, {device.MAX_BLOCK_DIM_Y}, {device.MAX_BLOCK_DIM_Z}")
    print(f"Max grid dimensions: {device.MAX_GRID_DIM_X}, {device.MAX_GRID_DIM_Y}, {device.MAX_GRID_DIM_Z}")
    print(f"Max shared memory per block: {device.MAX_SHARED_MEMORY_PER_BLOCK / 1024:.1f} KB")
    return True

def main():
    if not print_gpu_info():
        return
    
    print("\n🚀 Running Enhanced GPU Performance Tests...")
    
    # Test sizes (powers of 2)
    vector_sizes = [2**n for n in range(10, 25, 2)]  # Up to 2^24
    matrix_sizes = [2**n for n in range(5, 11)]      # Up to 2^10 (1024x1024)
    
    # Complex vector operations benchmarks
    vector_cpu_times = []
    vector_gpu_times = []
    print("\n📊 Complex Vector Operations Tests:")
    for size in vector_sizes:
        print(f"Testing size: {size:,}", end="")
        cpu_time, gpu_time = benchmark_complex_vector_ops(size)
        vector_cpu_times.append(cpu_time)
        vector_gpu_times.append(gpu_time)
        speedup = cpu_time / gpu_time
        print(f" - Speedup: {speedup:.2f}x")
    
    # Matrix multiplication benchmarks with shared memory
    matrix_cpu_times = []
    matrix_gpu_times = []
    print("\n📊 Matrix Multiplication Tests (With Shared Memory):")
    for size in matrix_sizes:
        print(f"Testing size: {size}x{size}", end="")
        cpu_time, gpu_time = benchmark_matrix_multiplication_shared(size)
        matrix_cpu_times.append(cpu_time)
        matrix_gpu_times.append(gpu_time)
        speedup = cpu_time / gpu_time
        print(f" - Speedup: {speedup:.2f}x")
    
    # Memory bandwidth benchmarks
    memory_cpu_times = []
    memory_gpu_times = []
    print("\n📊 Memory Bandwidth Tests:")
    for size in vector_sizes:
        print(f"Testing size: {size:,}", end="")
        cpu_time, gpu_time = benchmark_memory_bandwidth(size)
        memory_cpu_times.append(cpu_time)
        memory_gpu_times.append(gpu_time)
        speedup = cpu_time / gpu_time
        print(f" - Speedup: {speedup:.2f}x")
    
    # Combined stress test benchmarks
    combined_cpu_times = []
    combined_gpu_times = []
    print("\n📊 Combined Stress Tests:")
    for size in matrix_sizes:
        print(f"Testing size: {size}x{size}", end="")
        cpu_time, gpu_time = benchmark_combined_stress(size)
        combined_cpu_times.append(cpu_time)
        combined_gpu_times.append(gpu_time)
        speedup = cpu_time / gpu_time
        print(f" - Speedup: {speedup:.2f}x")
    
    # Plot results
    plot1 = plot_results(vector_sizes, vector_cpu_times, vector_gpu_times, 
                        "Complex Vector Operations")
    plot1.savefig('vector_performance.png')
    
    plot2 = plot_results(matrix_sizes, matrix_cpu_times, matrix_gpu_times, 
                        "Matrix Multiplication (Shared Memory)")
    plot2.savefig('matrix_performance.png')
    
    plot3 = plot_results(vector_sizes, memory_cpu_times, memory_gpu_times, 
                        "Memory Bandwidth")
    plot3.savefig('memory_performance.png')
    
    plot4 = plot_results(matrix_sizes, combined_cpu_times, combined_gpu_times, 
                        "Combined Stress Tests")
    plot4.savefig('combined_performance.png')
    
    print("\n✨ Tests completed! Performance plots saved with speedup curves")

if __name__ == "__main__":
    main()