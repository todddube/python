# Agentic Conversation Simulator

A multi-agent conversation simulator optimized for local Ollama LLM usage with GPU acceleration.

## Features

- Multiple AI agents with distinct personalities interacting in conversation
- Optimized for local Ollama usage with GPU acceleration
- Parallel processing of agent responses for better performance
- Resource monitoring (CPU, GPU, memory) during inference
- CarMax integration for vehicle searches
- Configurable conversation topics and agent selection

## Quick Start

1. Activate your virtual environment: `.venv\Scripts\activate`
2. Install dependencies: `python setup.py`
3. Start the app: `streamlit run agent_demo.py`

## Performance Optimization

This simulator is optimized to take advantage of your local GPU for faster inference:

- **GPU Acceleration**: Adjust the GPU utilization slider to control how much of the model runs on GPU vs CPU
- **Context Size**: Larger context allows for more conversation history but uses more memory
- **Thread Count**: Control CPU thread usage (0 = automatic detection)
- **Parallel Processing**: Agents now respond in parallel for better efficiency

## Performance Monitoring

Use the included monitoring tools to track performance:
- Run `python utils/monitor_ollama.py` in a separate terminal to log detailed metrics
- View live resource usage in the application sidebar
- Check logs in the `logs` directory for historical performance data