"""
Performance utilities for optimizing Ollama and agent performance
"""

import concurrent.futures
import psutil
import GPUtil
import time
from functools import wraps
from typing import List, Dict, Any, Callable, Optional

# Initialize performance metrics storage
performance_data = {
    'gpu_util': [],
    'cpu_util': [],
    'ram_util': [],
    'inference_times': [],
    'tokens_per_second': []
}

def measure_resource_usage(interval=2.0, max_samples=30):
    """
    Measure and return current system resource utilization
    
    Args:
        interval (float): Sampling interval in seconds
        max_samples (int): Maximum number of samples to keep in history
    
    Returns:
        dict: Current resource utilization metrics
    """
    # Get CPU usage
    cpu_percent = psutil.cpu_percent(interval=0.1)
    
    # Get RAM usage
    ram = psutil.virtual_memory()
    ram_percent = ram.percent
    
    # Get GPU usage if available
    try:
        gpus = GPUtil.getGPUs()
        gpu_percent = gpus[0].load * 100 if gpus else 0
    except:
        gpu_percent = 0
    
    # Store metrics in history with timestamp
    metrics = {
        'timestamp': time.time(),
        'cpu_percent': cpu_percent,
        'ram_percent': ram_percent,
        'gpu_percent': gpu_percent
    }
    
    # Update global performance data
    performance_data['gpu_util'].append(gpu_percent)
    performance_data['cpu_util'].append(cpu_percent)
    performance_data['ram_util'].append(ram_percent)
    
    # Keep only the most recent samples
    for key in ['gpu_util', 'cpu_util', 'ram_util']:
        if len(performance_data[key]) > max_samples:
            performance_data[key] = performance_data[key][-max_samples:]
            
    return metrics

def get_performance_history():
    """Get the collected performance metrics history"""
    return performance_data

def process_in_parallel(tasks: List[Dict], process_func: Callable, max_workers: Optional[int] = None):
    """
    Process multiple tasks in parallel using thread pool
    
    Args:
        tasks: List of task dictionaries to process
        process_func: Function to call for each task
        max_workers: Maximum number of parallel workers (None = auto)
        
    Returns:
        List of results in the same order as tasks
    """
    if max_workers is None:
        # Auto-determine optimal worker count based on CPU cores
        max_workers = min(len(tasks), psutil.cpu_count(logical=True) or 4)
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(process_func, **task): i for i, task in enumerate(tasks)
        }
        
        for future in concurrent.futures.as_completed(future_to_task):
            task_index = future_to_task[future]
            try:
                result = future.result()
                results.append((task_index, result))
            except Exception as e:
                results.append((task_index, f"Error: {str(e)}"))
                
    # Sort results back to original task order
    results.sort(key=lambda x: x[0])
    return [r[1] for r in results]

def performance_decorator(func):
    """
    Decorator to measure function execution time and resource usage
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        before_metrics = measure_resource_usage()
        
        result = func(*args, **kwargs)
        
        execution_time = time.time() - start_time
        after_metrics = measure_resource_usage()
        
        # Calculate resource usage during function execution
        delta_metrics = {
            'execution_time': execution_time,
            'cpu_delta': after_metrics['cpu_percent'] - before_metrics['cpu_percent'],
            'ram_delta': after_metrics['ram_percent'] - before_metrics['ram_percent'],
            'gpu_delta': after_metrics['gpu_percent'] - before_metrics['gpu_percent']
        }
        
        performance_data['inference_times'].append(execution_time)
        if len(performance_data['inference_times']) > 30:
            performance_data['inference_times'] = performance_data['inference_times'][-30:]
            
        return result
    
    return wrapper
