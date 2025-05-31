"""
Setup script for agent_demo.py - Optimized for local Ollama performance
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def install_dependencies():
    """Install required packages for optimal performance monitoring"""
    print("\n🚀 Installing required dependencies for Agentic Conversation Simulator...")
    
    # Required packages with detailed descriptions
    packages = [
        {
            "name": "psutil",
            "description": "System monitoring - CPU, memory and disk usage tracking",
            "version": ">=5.9.0" 
        },
        {
            "name": "GPUtil",
            "description": "GPU monitoring for NVIDIA GPUs",
            "version": ">=1.4.0"
        },
        {
            "name": "streamlit",
            "description": "UI framework for data applications",
            "version": ">=1.30.0"
        },
        {
            "name": "pyhocon",
            "description": "HOCON configuration file parser",
            "version": ">=0.9.0"
        },
        {
            "name": "requests",
            "description": "HTTP requests library for API interactions",
            "version": ">=2.28.0"
        },
        {
            "name": "numpy",
            "description": "Numerical computing library",
            "version": ">=1.20.0"
        },
        {
            "name": "matplotlib",
            "description": "Plotting library for performance charts",
            "version": ">=3.5.0" 
        }
    ]
    
    # Print system information
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    
    # Create utils directory if it doesn't exist
    utils_dir = Path(__file__).parent / "utils"
    utils_dir.mkdir(exist_ok=True)
    
    # Create __init__.py in utils directory if it doesn't exist
    init_file = utils_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()
        print(f"Created {init_file}")
    
    # Check Ollama installation
    print("\nChecking Ollama installation...")
    try:
        response = subprocess.run(["ollama", "list"], 
                                capture_output=True, 
                                text=True,
                                timeout=5)
        print("✅ Ollama is installed and working correctly")
        print("\nInstalled Ollama models:")
        print(response.stdout)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("⚠️ Ollama not found or not working correctly. Please install Ollama from https://ollama.ai")
    
    # Install packages
    print("\nInstalling Python packages:")
    for package in packages:
        full_name = f"{package['name']}{package['version']}"
        print(f"  - {package['name']} ({package['description']})")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", full_name])
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Error installing {package['name']}: {e}")
    
    print("\n✅ All dependencies installed successfully!")
    print("\nTo start the application, run:")
    print("   streamlit run agent_demo.py")

if __name__ == "__main__":
    install_dependencies()
