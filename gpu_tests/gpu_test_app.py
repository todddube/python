import streamlit as st
import numpy as np
from numba import cuda
import math
from timeit import default_timer as timer
import matplotlib.pyplot as plt
import pandas as pd
from gpu import (
    matrix_mul_shared_kernel,
    vector_ops_kernel,
    vector_ops_cpu,
    benchmark_complex_vector_ops,
    benchmark_matrix_multiplication_shared,
    benchmark_memory_bandwidth,
    benchmark_combined_stress,
    TILE_SIZE,
    MAX_TPB
)

# Test configurations
TEST_CONFIGS = {
    "Quick Test": {
        "warmup_runs": 1,
        "test_runs": 3,
        "max_size_power": 10
    },
    "Standard Test": {
        "warmup_runs": 3,
        "test_runs": 5,
        "max_size_power": 12
    },
    "Stress Test": {
        "warmup_runs": 5,
        "test_runs": 10,
        "max_size_power": 14
    }
}

# Test types with descriptions
TEST_TYPES = {
    "Vector Operations": "Trigonometric and sqrt operations on large vectors",
    "Matrix Multiplication": "Matrix multiplication using shared memory",
    "Memory Bandwidth": "Test memory transfer speeds with large arrays",
    "Combined Stress": "Multiple operations running in sequence"
}

def gpu_info():
    """Get information about available CUDA devices"""
    try:
        device = cuda.get_current_device()
        ctx = cuda.current_context()
        mem_free, mem_total = ctx.get_memory_info()
        return {
            "Name": device.name.decode(),
            "Max Threads Per Block": device.MAX_THREADS_PER_BLOCK,
            "Max Block Dimensions": f"{device.MAX_BLOCK_DIM_X}×{device.MAX_BLOCK_DIM_Y}×{device.MAX_BLOCK_DIM_Z}",
            "Max Grid Dimensions": f"{device.MAX_GRID_DIM_X}×{device.MAX_GRID_DIM_Y}×{device.MAX_GRID_DIM_Z}",
            "Free Memory (GB)": mem_free / (1024**3),
            "Total Memory (GB)": mem_total / (1024**3),
            "Compute Capability": f"{device.compute_capability[0]}.{device.compute_capability[1]}"
        }
    except cuda.CudaSupportError:
        return None

def run_tests(test_type, sizes, warmup_runs, test_runs, use_max_memory=False, memory_fraction=50):
    """Run selected performance tests with the specified configuration"""
    cpu_times = []
    gpu_times = []
    peak_memory = []
    progress_bar = st.progress(0)
    total_steps = len(sizes) * (warmup_runs + test_runs)
    step = 0
    
    # Reserve GPU memory if requested
    dummy_array = None
    if use_max_memory:
        try:
            ctx = cuda.current_context()
            total_mem = ctx.get_memory_info()[1]
            memory_size = int(total_mem * memory_fraction / 100)
            st.info(f"Reserving {memory_size / (1024**3):.2f} GB of GPU memory")
            # Create a dummy array to reserve memory
            dummy_array = np.ones(memory_size // 8, dtype=np.float64)
            # Transfer to GPU to actually reserve the memory
            d_dummy = cuda.to_device(dummy_array)
        except Exception as e:
            st.warning(f"Failed to reserve memory: {str(e)}")
    
    try:
        for i, size in enumerate(sizes):
            status_col1, status_col2 = st.columns(2)
            
            with status_col1:
                st.write(f"Testing size: {size:,}")
            
            # Warmup runs
            if warmup_runs > 0:
                for _ in range(warmup_runs):
                    # Clear GPU cache before each test
                    try:
                        cuda.current_context().deallocations.clear()
                    except:
                        pass
                    
                    if test_type == "Vector Operations":
                        _, _ = benchmark_complex_vector_ops(size)
                    elif test_type == "Matrix Multiplication":
                        _, _ = benchmark_matrix_multiplication_shared(size)
                    elif test_type == "Memory Bandwidth":
                        _, _ = benchmark_memory_bandwidth(size)
                    elif test_type == "Combined Stress":
                        _, _ = benchmark_combined_stress(size)
                    
                    step += 1
                    progress_bar.progress(step / total_steps)
            
            # Test runs
            cpu_times_size = []
            gpu_times_size = []
            peak_mem_size = []
            
            for _ in range(test_runs):
                # Clear GPU cache before each test
                try:
                    cuda.current_context().deallocations.clear()
                except:
                    pass
                
                # Run the test
                if test_type == "Vector Operations":
                    cpu_time, gpu_time = benchmark_complex_vector_ops(size)
                elif test_type == "Matrix Multiplication":
                    cpu_time, gpu_time = benchmark_matrix_multiplication_shared(size)
                elif test_type == "Memory Bandwidth":
                    cpu_time, gpu_time = benchmark_memory_bandwidth(size)
                elif test_type == "Combined Stress":
                    cpu_time, gpu_time = benchmark_combined_stress(size)
                    
                cpu_times_size.append(cpu_time)
                gpu_times_size.append(gpu_time)
                
                # Get peak memory usage
                ctx = cuda.current_context()
                mem_free, mem_total = ctx.get_memory_info()
                peak_mem_size.append((mem_total - mem_free) / (1024**3))  # Convert to GB
                
                step += 1
                progress_bar.progress(step / total_steps)
            
            # Average results for this size
            cpu_time_avg = np.mean(cpu_times_size)
            gpu_time_avg = np.mean(gpu_times_size)
            peak_mem_avg = np.max(peak_mem_size)  # Use maximum peak memory
            
            cpu_times.append(cpu_time_avg)
            gpu_times.append(gpu_time_avg)
            peak_memory.append(peak_mem_avg)
            
            with status_col2:
                st.write(f"CPU Time: {cpu_time_avg:.4f}s")
                st.write(f"GPU Time: {gpu_time_avg:.4f}s")
                st.write(f"Speedup: {cpu_time_avg/gpu_time_avg:.2f}x")
                st.write(f"Peak Memory: {peak_mem_avg:.2f} GB")
    
    finally:
        # Clean up dummy array reference
        if dummy_array is not None:
            del dummy_array
        
        # Force garbage collection to release GPU memory
        import gc
        gc.collect()
        
        # Clear CUDA cache
        try:
            cuda.current_context().deallocations.clear()
        except:
            pass
    
    return cpu_times, gpu_times, peak_memory

def plot_results(sizes, cpu_times, gpu_times, peak_memory, operation):
    """Create performance comparison plots"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Performance plot
    ax1.plot(sizes, cpu_times, 'o-', label='CPU', color='blue')
    ax1.plot(sizes, gpu_times, 'o-', label='GPU', color='red')
    speedups = [cpu_times[i]/gpu_times[i] for i in range(len(sizes))]
    ax1.plot(sizes, speedups, 'g--', label='Speedup', alpha=0.5)
    ax1.set_xlabel('Size')
    ax1.set_ylabel('Time (seconds)')
    ax1.set_title(f'CPU vs GPU Performance: {operation}')
    ax1.legend()
    ax1.grid(True)
    ax1.set_yscale('log')
    ax1.set_xscale('log')
    
    # Memory usage plot
    ax2.plot(sizes, peak_memory, 'o-', label='Peak Memory', color='purple')
    ax2.set_xlabel('Size')
    ax2.set_ylabel('Memory Usage (GB)')
    ax2.set_title('GPU Memory Usage')
    ax2.legend()
    ax2.grid(True)
    ax2.set_xscale('log')
    
    plt.tight_layout()
    return fig

def main():
    st.title("🚀 GPU Performance Testing Dashboard")
      # GPU Information
    st.header("🎯 GPU Specifications")
    gpu_data = gpu_info()
    if not gpu_data:
        st.error("No CUDA-capable GPU detected!")
        return
    
    # Create three columns for GPU specs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("💻 Hardware Info")
        st.markdown(f"""
        **GPU Name**  
        {gpu_data['Name']}
        
        **Compute Capability**  
        CUDA {gpu_data['Compute Capability']}
        
        **Memory**  
        Free: {gpu_data['Free Memory (GB)']:.2f} GB  
        Total: {gpu_data['Total Memory (GB)']:.2f} GB
        """)
    
    with col2:
        st.info("🧮 Compute Specs")
        st.markdown(f"""
        **Threads Per Block**  
        {gpu_data['Max Threads Per Block']}
        
        **Block Dimensions**  
        {gpu_data['Max Block Dimensions']}
        """)
    
    with col3:
        st.info("🌐 Grid Info")
        st.markdown(f"""
        **Grid Dimensions**  
        {gpu_data['Max Grid Dimensions']}
        
        **Memory Usage**  
        {(gpu_data['Total Memory (GB)'] - gpu_data['Free Memory (GB)']):.2f} GB Used  
        {(gpu_data['Free Memory (GB)'] / gpu_data['Total Memory (GB)'] * 100):.1f}% Free
        """)
    
    # Add memory usage progress bar
    memory_usage = (gpu_data['Total Memory (GB)'] - gpu_data['Free Memory (GB)']) / gpu_data['Total Memory (GB)']
    st.progress(memory_usage, text="Memory Usage")
      # Move configurations to sidebar
    with st.sidebar:
        st.header("⚙️ Test Configuration")
        
        # Test Type Selection
        test_type = st.selectbox(
            "Select Test Type",
            list(TEST_TYPES.keys())
        )
        st.info(TEST_TYPES[test_type])
        
        # Test Profile Selection
        st.subheader("Test Profile")
        test_profile = st.selectbox(
            "Select Profile",
            list(TEST_CONFIGS.keys())
        )
        st.info(f"📊 Profile Settings:\n"
                f"• Warmup runs: {TEST_CONFIGS[test_profile]['warmup_runs']}\n"
                f"• Test runs: {TEST_CONFIGS[test_profile]['test_runs']}\n"
                f"• Max size: 2^{TEST_CONFIGS[test_profile]['max_size_power']}")
        
        # Advanced Settings in Sidebar
        st.subheader("🔧 Advanced Settings")
        custom_warmup = st.number_input(
            "Warmup Runs",
            min_value=0,
            max_value=10,
            value=TEST_CONFIGS[test_profile]["warmup_runs"],
            help="Number of warmup runs before actual testing"
        )
        
        custom_runs = st.number_input(
            "Test Runs",
            min_value=1,
            max_value=20,
            value=TEST_CONFIGS[test_profile]["test_runs"],
            help="Number of test iterations for averaging"
        )
        
        use_max_memory = st.checkbox(
            "Maximum Memory Usage", 
            value=False,
            help="Enable to use maximum available GPU memory"
        )
        
        if use_max_memory:
            memory_fraction = st.slider(
                "Memory Usage (%)", 
                min_value=10, 
                max_value=90, 
                value=50,
                help="Percentage of total GPU memory to use"
            )
          # Size Configuration in Sidebar
        st.subheader("📏 Size Configuration")
        min_size_power = 8  # Minimum size to avoid under-utilization
        max_size_power = min(
            TEST_CONFIGS[test_profile]["max_size_power"],
            14 if use_max_memory else 12
        )
        
        size_range = st.slider(
            "Size Range (power of 2)" if test_type == "Vector Operations"
            else "Matrix Size Range (power of 2)",
            min_value=min_size_power,
            max_value=max_size_power,
            value=(min_size_power, max_size_power-2),
            step=1,
            help="Select the range of sizes to test (powers of 2)"
        )
        sizes = [2**n for n in range(size_range[0], size_range[1] + 1)]
        
        # Show size examples
        st.caption("Test sizes:")
        size_examples = [f"• 2^{n} = {2**n:,}" for n in range(size_range[0], size_range[1] + 1)]
        st.text("\n".join(size_examples))
        
        # Memory Usage Estimate
        st.subheader("💾 Memory Estimate")
        max_size = max(sizes)
        if test_type == "Matrix Multiplication":
            mem_needed = (3 * max_size * max_size * 4) / (1024**3)  # 3 matrices, float32
            st.warning(f"Peak memory: {mem_needed:.2f} GB\n"
                      f"Matrix size: {max_size}×{max_size}")
        else:
            mem_needed = (4 * max_size * 4) / (1024**3)  # 4 vectors, float32
            st.warning(f"Peak memory: {mem_needed:.2f} GB\n"
                      f"Vector size: {max_size:,}")
    
    # Run Tests
    if st.button("Run Performance Tests"):
        st.subheader("🔄 Running Tests...")
        try:
            warmup_runs = custom_warmup if 'custom_warmup' in locals() else TEST_CONFIGS[test_profile]["warmup_runs"]
            test_runs = custom_runs if 'custom_runs' in locals() else TEST_CONFIGS[test_profile]["test_runs"]
            use_memory = use_max_memory if 'use_max_memory' in locals() else False
            memory_frac = memory_fraction if 'memory_fraction' in locals() else 50
            
            cpu_times, gpu_times, peak_memory = run_tests(
                test_type, sizes,
                warmup_runs, test_runs,
                use_memory, memory_frac
            )
            
            # Plot Results
            st.subheader("📈 Performance Results")
            fig = plot_results(sizes, cpu_times, gpu_times, peak_memory, test_type)
            st.pyplot(fig)
            
            # Results Table
            st.subheader("📋 Detailed Results")
            results_df = pd.DataFrame({
                'Size': sizes,
                'CPU Time (s)': cpu_times,
                'GPU Time (s)': gpu_times,
                'Speedup (x)': [cpu_times[i]/gpu_times[i] for i in range(len(sizes))],
                'Peak Memory (GB)': peak_memory
            })
            st.dataframe(results_df)
            
        except Exception as e:
            st.error(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    main()
