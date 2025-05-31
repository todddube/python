"""
Monitors Ollama performance and logs resource usage.
Run this alongside the agent_demo.py to collect more detailed performance metrics.
"""

import time
import json
import os
import psutil
import datetime
import argparse
import sys
import threading
from pathlib import Path

# Try to import GPU monitoring libraries
try:
    import GPUtil
    HAS_GPU = True
except ImportError:
    HAS_GPU = False
    print("GPUtil not installed. GPU monitoring disabled.")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("Requests not installed. Ollama API monitoring disabled.")

# Set up logging
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"ollama_perf_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

# Global variables
running = True
POLL_INTERVAL = 1.0  # seconds

def get_ollama_stats():
    """Get statistics from Ollama API"""
    if not HAS_REQUESTS:
        return {}
        
    try:
        # Get Ollama version
        response = requests.get('http://localhost:11434/api/version', timeout=2)
        if response.status_code != 200:
            return {"status": "error", "message": f"HTTP {response.status_code}"}
            
        version_data = response.json()
        
        # Try to get memory usage info from a simple generation request
        # This is a very small request just to get metrics
        try:
            response = requests.post('http://localhost:11434/api/generate', 
                json={
                    "model": "llama3",
                    "prompt": "test",
                    "raw": True,
                    "stream": False,
                    "options": {"num_predict": 1}
                },
                timeout=5
            )
            if response.status_code == 200:
                metrics = response.json()
                return {
                    "status": "ok",
                    "version": version_data.get('version', 'unknown'),
                    "eval_count": metrics.get('eval_count', 0),
                    "eval_duration": metrics.get('eval_duration', 0),
                    "tokens_per_second": metrics.get('eval_count', 0) / (metrics.get('eval_duration', 1) / 1e9) if metrics.get('eval_duration', 0) > 0 else 0
                }
        except Exception as e:
            pass
            
        return {
            "status": "ok",
            "version": version_data.get('version', 'unknown')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_system_stats():
    """Get system resource usage"""
    stats = {
        "timestamp": datetime.datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_used_gb": psutil.virtual_memory().used / (1024**3)
    }
    
    if HAS_GPU:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Get primary GPU
                stats.update({
                    "gpu_name": gpu.name,
                    "gpu_load": gpu.load * 100,
                    "gpu_memory_used": gpu.memoryUsed,
                    "gpu_memory_total": gpu.memoryTotal,
                    "gpu_memory_percent": gpu.memoryUtil * 100,
                    "gpu_temperature": gpu.temperature
                })
        except Exception as e:
            stats["gpu_error"] = str(e)
    
    return stats

def monitor_loop():
    """Main monitoring loop"""
    global running
    
    # Write CSV header
    with open(LOG_FILE, 'w') as f:
        f.write("timestamp,cpu_percent,memory_percent,memory_used_gb,gpu_load,gpu_memory_percent,gpu_temperature,ollama_status,ollama_tokens_per_second\n")
    
    print(f"Starting Ollama performance monitoring. Logs saved to: {LOG_FILE}")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        while running:
            system_stats = get_system_stats()
            ollama_stats = get_ollama_stats()
            
            # Combine stats
            stats = {**system_stats}
            
            if ollama_stats.get('status') == 'ok':
                stats['ollama_status'] = 'running'
                stats['ollama_tokens_per_second'] = ollama_stats.get('tokens_per_second', 0)
            else:
                stats['ollama_status'] = 'error'
                stats['ollama_tokens_per_second'] = 0
            
            # Write to CSV
            with open(LOG_FILE, 'a') as f:
                f.write(f"{stats['timestamp']},{stats['cpu_percent']},{stats['memory_percent']},{stats['memory_used_gb']}," + 
                       f"{stats.get('gpu_load', 'NA')},{stats.get('gpu_memory_percent', 'NA')},{stats.get('gpu_temperature', 'NA')}," +
                       f"{stats['ollama_status']},{stats['ollama_tokens_per_second']}\n")
            
            # Print current stats
            print(f"\rCPU: {stats['cpu_percent']:.1f}% | RAM: {stats['memory_percent']:.1f}% | " +
                  f"GPU: {stats.get('gpu_load', 'NA'):.1f}% | Ollama: {stats['ollama_status']} | " +
                  f"Tokens/sec: {stats.get('ollama_tokens_per_second', 0):.2f}", end="")
            
            time.sleep(POLL_INTERVAL)
    
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"\nError in monitoring loop: {e}")
    finally:
        print(f"\nPerformance log saved to: {LOG_FILE}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor Ollama performance and resource usage")
    parser.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds")
    args = parser.parse_args()
    
    POLL_INTERVAL = args.interval
    
    # Create a thread to handle monitoring
    monitor_thread = threading.Thread(target=monitor_loop)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    try:
        # Keep main thread alive to handle keyboard interrupts
        while monitor_thread.is_alive():
            monitor_thread.join(0.5)
    except KeyboardInterrupt:
        print("\nShutting down...")
        running = False
        monitor_thread.join(2.0)
    except Exception as e:
        print(f"Error: {e}")
        running = False
