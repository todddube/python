from time import sleep
from time import time
import webbrowser
import threading
import os
import subprocess
import streamlit as st
import requests
import pyhocon
import time as py_time  # Import time with alias to avoid conflict
import concurrent.futures
from functools import partial
import sys
from collections import deque
from typing import List, Dict, Any, Optional

# Add version constants at top of file
__version__ = "0.2"
__author__ = "Todd Dube"

# Initialize performance metrics in session state
if 'performance_metrics' not in st.session_state:
    st.session_state.performance_metrics = {
        'last_inference_time': 0,
        'average_inference_time': 0,
        'tokens_per_second': 0,
        'total_tokens': 0,
        'model': "llama3"
    }

# Add path for utils module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from utils.performance import measure_resource_usage, process_in_parallel, get_performance_history, performance_decorator
except ImportError:
    # If import fails, create a simplified version of needed functions
    def measure_resource_usage():
        return {'cpu_percent': 0, 'gpu_percent': 0, 'ram_percent': 0}
    
    def process_in_parallel(tasks, process_func, max_workers=None):
        results = []
        for task in tasks:
            results.append(process_func(**task))
        return results
    
    def get_performance_history():
        return {'gpu_util': [], 'cpu_util': [], 'ram_util': [], 'inference_times': []}
    
    def performance_decorator(func):
        return func

class CarmaxSearchAgent:
    def __init__(self, max_price=None, min_price=None):
        self.base_url = "https://www.carmax.com/cars"
        self.max_price = max_price
        self.min_price = min_price

    def search_vehicles(self, query):
        """Search Carmax for vehicles matching query"""
        # updated to use carmax search URL
        try:
            url = f"{self.base_url}?search={query}&showreservedcars=false"
            if self.max_price:
                url += f"&price-max={self.max_price}"
            if self.min_price:
                url += f"&price-min={self.min_price}"
                
            webbrowser.open(url)
            return f"➡️🎯Opening Carmax search for: {query}"
            
        except Exception as e:
            return f"Error searching Carmax: {str(e)}"

    def get_recommendations(self, preferences):
        """Get vehicle recommendations based on preferences"""
        prompt = f"""
        Based on these preferences: {preferences}
        Suggest 3 specific vehicle models available at Carmax.
        Include year ranges and price estimates.
        """
        return get_ollama_response(prompt)


def open_chromium():
    """Open Chromium browser and navigate to Streamlit app."""
    chromium_path = r"C:\Program Files\Chromium\chrome.exe"  # Adjust path as needed
    url = "http://localhost:8501"  # Default Streamlit port
    
    try:
        # Start Chromium
        webbrowser.register('chromium', None, 
                           webbrowser.BackgroundBrowser(chromium_path))
        webbrowser.get('chromium').open(url) 
    except Exception as e:
        print(f"Error opening Chromium: {e}")
        # Fallback to default browser
        webbrowser.open(url)

def get_ollama_response(prompt, model="llama3", num_ctx=4096, num_gpu=100, num_thread=0, mirostat=0):
    """
    Get response from Ollama API with optimized parameters for local GPU/CPU usage
    
    Args:
        prompt: The text prompt to send to the model
        model: The Ollama model to use (default: llama3)
        num_ctx: Context window size (default: 4096)
        num_gpu: Percentage of layers to offload to GPU (0-100) (default: 100 for full GPU utilization)
        num_thread: Number of threads to use (0 means auto) (default: 0)
        mirostat: Mirostat sampling algorithm (0 = off, 1 = v1, 2 = v2) (default: 0)
    
    Returns:
        The generated text response
    """
    start_time = time()
    try:
        response = requests.post('http://localhost:11434/api/generate',
                               json={
                                   "model": model,
                                   "prompt": prompt,
                                   "system": "",
                                   "stream": False,
                                   "temperature": 0.7,
                                   "options": {
                                       "num_ctx": num_ctx,           # Larger context window
                                       "num_gpu": num_gpu,           # Percentage of layers to run on GPU
                                       "num_thread": num_thread,     # Auto-detect optimal thread count (0 = auto)
                                       "mirostat": mirostat,         # Advanced sampling algorithm
                                       "repeat_penalty": 1.1,        # Penalize repetition for better text generation
                                       "num_predict": 512,           # Increase tokens to generate
                                       "seed": -1                    # Random seed for reproducibility (-1 = random seed)
                                   }
                               })
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        json_response = response.json()
        
        # Calculate and store performance metrics
        inference_time = time() - start_time
        if 'eval_count' in json_response:
            tokens_generated = json_response.get('eval_count', 0)
            tokens_per_second = tokens_generated / inference_time if inference_time > 0 else 0
            st.session_state.performance_metrics = {
                'last_inference_time': inference_time,
                'tokens_per_second': tokens_per_second,
                'model': model
            }
            
        if 'response' in json_response:
            return json_response['response']
        else:
            raise KeyError("Key 'response' not found in the API response.")

    except requests.exceptions.RequestException as e:
        return f"Error get_ollama_response: Failed to connect to the API. {e}"
    except KeyError as e:
        return f"Error get_ollama_response: {e}"

class VehicleAgent:
    """Agent for handling vehicle-related tasks."""
    def __init__(self, max_price=None, min_price=None):
        self.carmax = CarmaxSearchAgent(max_price, min_price)
        # Add vehicle agent status to sidebar
        st.sidebar.markdown("""
            <style>
            @keyframes colorChange {
            0% { color: #FF0000; }
            25% { color: #00FF00; }
            50% { color: #0000FF; }
            75% { color: #FF00FF; }
            100% { color: #FF0000; }
            }
            .animated-text {
            animation: colorChange 4s infinite;
            font-weight: bold;
            }
            </style>
            <h3><span class="animated-text">🚗 Vehicle Agent....</span></h3>
        """, unsafe_allow_html=True)
        # st.write("Searches CarMax inventory and extracts vehicle mentions")
        #st.sidebar.markdown("🔎  Online")
        
    def extract_mentions(self, text):
        """Extract vehicle brands and models from text."""
        prompt = f"""
        Analyze this text and extract any car brands and their models.
        Return only valid brand-model pairs, one per line.
        Text: {text}
        Format each line as: brand|model
        Examples: toyota|camry, honda|civic
        """
        response = get_ollama_response(prompt)
        vehicle_pairs = []
        
        # Process response into pairs
        for line in response.split('\n'):
            if '|' in line:
                brand, model = line.strip().split('|')
                if brand and model:
                    vehicle_pairs.append(f"{brand.strip()} {model.strip()}")
        
        return vehicle_pairs

    def analyze_conversation(self, conversation):
        """Analyze conversation for vehicle mentions."""
        vehicle_mentions = []
        for _, msg in conversation:
            pairs = self.extract_mentions(msg)
            vehicle_mentions.extend(pairs)
        return list(set(vehicle_mentions))  # Remove duplicates

    def search_vehicles(self, vehicles):
        """Search for vehicles on Carmax."""
        if not vehicles:
            return None
        search_query = ", ".join(vehicles)
        return self.carmax.search_vehicles(search_query)

class Agent:
    """Agents class defining agent name and personality."""
    
    # Default avatar for unknown agent types
    DEFAULT_AVATAR = "👤"
    
    def __init__(self, name, personality, kind, avatar=None):
        self.name = name
        self.personality = personality
        self.kind = kind
        self.avatar = avatar or self.DEFAULT_AVATAR
        self.conversation_history = []
        # Set default model parameters for this agent
        self.model_params = {
            "model": "llama3",   # Default model
            "num_ctx": 4096,     # Context window size
            "num_gpu": 100,      # Use 100% of GPU by default
            "num_thread": 0,     # Auto-detect optimal thread count
            "mirostat": 0        # Advanced sampling algorithm (0 = disabled)
        }

    def __getattr__(self, name):
        # Handle missing attributes gracefully
        if name in self.__dict__:
            return self.__dict__[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    @performance_decorator
    def respond(self, message):
        """Generate response using the Ollama API with optimized parameters"""
        context = f"""
        You are {self.name}. {self.personality}
        Previous conversation: {self.conversation_history}
        Respond to: {message}
        Keep response brief and in character.
        """
        response = get_ollama_response(
            prompt=context,
            model=self.model_params["model"],
            num_ctx=self.model_params["num_ctx"],
            num_gpu=self.model_params["num_gpu"],
            num_thread=self.model_params["num_thread"],
            mirostat=self.model_params["mirostat"]
        )
        self.conversation_history.append(f"{self.name}: {response}")
        return response
        
    @staticmethod
    def respond_parallel(agents, message):
        """Process agent responses in parallel to maximize efficiency"""
        tasks = []
        for agent in agents:
            tasks.append({
                "agent": agent,
                "message": message
            })
            
        def _process_agent_response(agent, message):
            response = agent.respond(message)
            return (agent, response)
        
        # Determine optimal worker count based on available CPU cores
        optimal_workers = min(len(agents), os.cpu_count() or 2)
        
        # Process responses in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=optimal_workers) as executor:
            futures = []
            for task in tasks:
                futures.append(
                    executor.submit(_process_agent_response, task["agent"], task["message"])
                )
            
            # Collect results as they complete
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    agent, response = future.result()
                    results.append((agent, response))
                except Exception as e:
                    st.error(f"Error in parallel agent response: {str(e)}")
            
        return results

    def get_config():
        """Load and return configuration from HOCON file."""
        try:
            # Get the directory of the current script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, 'agents_config.hocon')
            config = pyhocon.ConfigFactory.parse_file(config_path)
            # Create empty list to store all agents
            agents = []
                        
            # Iterate through all agent configs and create agents
            for agent_key in config['agents']:
                agent_config = config['agents'][agent_key]
                agent = Agent(
                    name=agent_config['name'],
                    personality=agent_config['personality'],
                    kind=agent_config['kind'],
                    # Use get() with None as default for optional avatar
                    avatar=agent_config.get('avatar', None)
                )
                agents.append(agent)

            # Get conversation starters
            conversation_starters = config['conversation.starters']
            
            return agents, conversation_starters
        except Exception as e:
            raise Exception(f"Error loading configuration: {e}")
        
def setup_agents(agents):
    # Display agents status in sidebar
    with st.sidebar.expander("👥 Agents & Personalities", expanded=False):
        for agent in agents:
            st.markdown(f"**{agent.avatar} {agent.name}**")
            st.write(agent.personality)
            st.markdown("---")

def init_streamlit():
    """Initialize Streamlit configuration and check services."""
    try:
        # Set page config first
        st.set_page_config(
            page_title="Agentic Conversation Simulator",
            page_icon="🚗",
            layout="wide",
            initial_sidebar_state="auto"
        )
        
        # Add menu items to sidebar explicitly
        with st.sidebar:
            with st.expander("🏈 Menu", expanded=False):
                st.markdown("### Help")
                st.markdown("[GitHub Repository](https://github.com/todddube)")
                st.markdown("### Report Issues")
                st.markdown("[Submit Bug Report](https://github.com/todddube/python/issues)")
                st.markdown("### About")
                st.markdown("""
                    # Agentic Conversation Simulator
                    
                    A multi-agent conversation simulator using Ollama LLM.
                    
                    * Multiple AI agents with distinct personalities
                    * CarMax integration for vehicle searches
                    * Configurable conversation topics
                    """)
       
    except Exception as e:
        st.warning("⚠️ Error initializing Streamlit configuration")
        print(f"Error in init_streamlit: {e}")

def create_sidebar_conversation_animation():
    """
    Creates an animated conversation display in the sidebar showing agents talking to each other.
    This function sets up the CSS for animation and creates a placeholder for the animation.
    """
    # Add the animation CSS to the sidebar
    st.sidebar.markdown("""
        <style>
        @keyframes slideInRight {
            0% { transform: translateX(100%); opacity: 0; }
            100% { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideInLeft {
            0% { transform: translateX(-100%); opacity: 0; }
            100% { transform: translateX(0); opacity: 1; }
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        .chat-bubble-right {
            background-color: #e1f5fe;
            border-radius: 15px;
            padding: 8px 12px;
            margin: 5px 0 5px auto;
            max-width: 80%;
            animation: slideInRight 0.5s ease-out, pulse 2s infinite;
            position: relative;
        }
        .chat-bubble-left {
            background-color: #f0f4c3;
            border-radius: 15px;
            padding: 8px 12px;
            margin: 5px auto 5px 0;
            max-width: 80%;
            animation: slideInLeft 0.5s ease-out, pulse 2s infinite;
            position: relative;
        }
        .agent-name {
            font-weight: bold;
            font-size: 0.8em;
            margin-bottom: 2px;
        }
        .chat-container {
            max-height: 300px;
            overflow-y: auto;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 10px;
            background-color: #f9f9f9;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create a container for the animation in the sidebar
    st.sidebar.markdown("### 🎬 Live Agent Conversation")
    chat_container = st.sidebar.empty()
    
    # Return the container for later updates
    return chat_container

def update_sidebar_animation(container, speakers, messages):
    """
    Updates the sidebar animation with new conversation messages.
    
    Args:
        container: The Streamlit container to update
        speakers: List of speaker names with their avatars
        messages: List of message strings
    """
    html_content = '<div class="chat-container">'
    
    for i, (speaker, msg) in enumerate(zip(speakers, messages)):
        # Alternate between left and right bubbles
        bubble_class = "chat-bubble-left" if i % 2 == 0 else "chat-bubble-right"
        
        # Create the chat bubble
        html_content += f"""
        <div class="{bubble_class}">
            <div class="agent-name">{speaker}</div>
            {msg[:100] + '...' if len(msg) > 100 else msg}
        </div>
        """
    
    html_content += '</div>'
    container.markdown(html_content, unsafe_allow_html=True)

def ollama_check():
    """Check if the Ollama service is running and show optimization status."""
    
    # Add status check for Ollama service
    try:
        response = requests.get('http://localhost:11434/api/version')
        if response.status_code == 200:
            version_data = response.json()
            version = version_data.get('version', 'unknown')
            
            st.sidebar.markdown(f"""
                <style>
                @keyframes flashingColors {{
                    0% {{ color: #FF0000; }}
                    25% {{ color: #00FF00; }}
                    50% {{ color: #0000FF; }}
                    75% {{ color: #FFFF00; }}
                    100% {{ color: #FF0000; }}
                }}
                .flashing-text {{
                    animation: flashingColors 2s infinite;
                    font-weight: bold;
                }}
                </style>
                <span class="flashing-text">🟢 Ollama service is running</span> (v{version})
            """, unsafe_allow_html=True)
            
            # Try to determine if CUDA is available
            has_gpu = False
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_info = gpus[0]
                    has_gpu = True
                    st.sidebar.markdown(f"🖥️ **GPU: {gpu_info.name}**")
                    st.sidebar.progress(gpu_info.load, f"GPU Load: {gpu_info.load*100:.1f}%")
            except:
                pass
                
            if has_gpu:
                st.sidebar.success("✅ GPU acceleration available")
            else:
                st.sidebar.warning("⚠️ No GPU detected, using CPU only")
                
        else:
            st.sidebar.error("🔴 Ollama service is not responding properly")
            st.error("Ollama service is not responding properly. Please check if it's running correctly.")
    except requests.exceptions.RequestException:
        st.sidebar.error("🔴 Ollama service is not running")
        st.error("Ollama service is not running. Please start Ollama first.")

    # Check model availability with expanded details
    with st.sidebar.expander("🤖 Available Models"):
        try:
            response = requests.get('http://localhost:11434/api/tags')
            if response.status_code == 200:
                models = response.json()
                if 'models' in models and models['models']:
                    for model in models['models']:
                        model_name = model.get('name', 'unknown')
                        model_size = model.get('size', 0) / (1024 * 1024 * 1024)  # Convert to GB
                        st.write(f"- **{model_name}** ({model_size:.1f}GB)")
                else:
                    st.write("No models found. Try pulling a model with:")
                    st.code("ollama pull llama3", language="bash")
        except requests.exceptions.RequestException:
            st.warning("⚠️ Cannot fetch available models")
            
    # Show optimization recommendations
    with st.sidebar.expander("🚀 Optimization Tips"):
        st.markdown("""
        **For best performance:**
        - Use smaller models if latency is important
        - Increase GPU utilization to 100% if dedicated GPU available
        - For multi-agent conversations, use parallel processing
        - Monitor GPU/CPU usage to find optimal settings
        """)
        
    # Add resource monitoring in sidebar
    metrics = measure_resource_usage()
    with st.sidebar.expander("📊 System Resources", expanded=False):
        cpu_col, gpu_col = st.columns(2)
        with cpu_col:
            st.metric("CPU Usage", f"{metrics['cpu_percent']:.1f}%")
        with gpu_col:
            st.metric("GPU Usage", f"{metrics['gpu_percent']:.1f}%")
        st.progress(metrics['ram_percent']/100, f"RAM: {metrics['ram_percent']:.1f}%")


def main():
    """Main function to run the Streamlit app."""
    # Continue with existing main function
    ollama_check()
    
    # Get agents and topics
    try:
        agents, conversation_starters = Agent.get_config()
        setup_agents(agents)
    except Exception as e:
        st.error(f"Error loading agents: {str(e)}")
        return
    
    st.title("Agentic Conversation Simulator")
    # Add goodbye button in a container at the top right
    if st.button("👋 Exit", type="primary"):
        st.markdown("""
            <div style="text-align: center; margin-top: 50px;">
                <h1>👋 Goodbye!</h1>
                <p style="font-size: 24px;">Thanks for using the Agentic Conversation Simulator</p>
                <p style="font-size: 20px;">Feel free to close this window</p>
            </div>
        """, unsafe_allow_html=True)
        st.balloons()  # Add a fun effect
        st.stop()  # Stop execution here
    # Initialize session state
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
        
    # Get agents and topics
    try:
        agents, conversation_starters = Agent.get_config()
    
         # Agent selector
        selected_agents = st.multiselect(
            "Select agents to participate (minimum 2):",
            options=[agent.name for agent in agents],
            default=[agents[0].name, agents[1].name]
        )

        # Validate minimum number of agents
        if len(selected_agents) < 2:
            st.error("Please select at least 2 agents to continue")
            return
    
        # Topic selector with option for custom input
        topic_source = st.radio("Choose topic source:", ["Predefined Topics", "Custom Topic"])
        if topic_source == "Predefined Topics":
            topic = st.selectbox("Select a conversation topic:", conversation_starters)
        else:
            topic = st.text_input("Enter a custom conversation topic:", "")
            if not topic:
                st.error("Please enter a topic to continue")
                return
        
          # Get number of iterations from user
        num_iterations = st.number_input("Number of conversation rounds:", min_value=1, max_value=10, value=1)
        
        # Filter agents based on selection while maintaining order
        ordered_agents = []
        for name in selected_agents:
            agent = next(a for a in agents if a.name == name)
            ordered_agents.append(agent)
        agents = ordered_agents
        
        # Update sidebar with selected agents status
        st.sidebar.markdown("### Selected Agents Status")
        for agent in agents:  # Using ordered agents list
            st.sidebar.markdown(f"{agent.avatar} 🟢 {agent.name} ready")
        st.sidebar.markdown("---")
        
        # Create animated conversation display in the sidebar
        chat_container = create_sidebar_conversation_animation()
          # Add a selection box for Ollama model
        available_models = ["llama3", "llama3:8b", "mistral", "codellama", "phi3"]  # Default models
        # Try to get real model list
        try:
            response = requests.get('http://localhost:11434/api/tags')
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model['name'] for model in models_data.get('models', [])]
        except:
            pass  # Use default model list on failure
            
        col1, col2 = st.columns(2)
        with col1:
            selected_model = st.selectbox("Select Ollama model:", available_models, index=0)
        with col2:
            # GPU utilization slider (0 = CPU only, 100 = full GPU)
            gpu_utilization = st.slider("GPU utilization %:", 0, 100, 100, 5)
        
        # Add advanced options in expander
        with st.expander("Advanced Performance Options", expanded=False):
            context_size = st.slider("Context size:", 1024, 8192, 4096, 512)
            thread_count = st.slider("CPU Thread count (0=auto):", 0, 16, 0, 1)
            batch_size = st.slider("Batch size:", 1, 512, 32, 8)
        
        # Update all agents with selected model
        for agent in agents:
            agent.model_params["model"] = selected_model
            agent.model_params["num_gpu"] = gpu_utilization
            agent.model_params["num_ctx"] = context_size
            agent.model_params["num_thread"] = thread_count
            
        if st.button("Start Conversation"):
            # Create vehicle agent first, before starting conversation
            vehicle_agent = VehicleAgent()
            
            st.session_state.conversation = []  # Clear previous conversation
            st.subheader(f"Topic: {topic}")
            
            # Create placeholder for conversation
            conversation_placeholder = st.empty()
            
            # Create performance monitoring container
            perf_container = st.empty()
            
            # Iterate the specified number of times
            for iteration in range(num_iterations):
                # Process all agents in parallel for better performance
                with st.spinner(f"Processing responses for round {iteration+1}/{num_iterations}..."):
                    # Get current resource usage before processing
                    before_metrics = measure_resource_usage()
                    
                    # Process agents in parallel
                    responses = Agent.respond_parallel(agents, topic)
                    
                    # Get resource usage after processing
                    after_metrics = measure_resource_usage()
                    
                    # Add responses to conversation
                    for agent, response in responses:
                        st.session_state.conversation.append((f"{agent.avatar} {agent.name}", response))
                        
                    # Update display
                    with conversation_placeholder.container():
                        for speaker, msg in st.session_state.conversation:
                            st.markdown(f"**{speaker}**:")
                            st.markdown(f">{msg}", unsafe_allow_html=True)
                            st.markdown("---")
                    
                    # Update sidebar animation
                    speakers = [speaker for speaker, _ in st.session_state.conversation]
                    messages = [msg for _, msg in st.session_state.conversation]
                    update_sidebar_animation(chat_container, speakers, messages)
                    
                    # Update performance metrics
                    perf_history = get_performance_history()
                    perf_metrics = st.session_state.performance_metrics
                    
                    # Display performance metrics
                    with perf_container.container():
                        perf_col1, perf_col2, perf_col3 = st.columns(3)
                        with perf_col1:
                            st.metric("GPU Usage", f"{after_metrics['gpu_percent']:.1f}%", 
                                      f"{after_metrics['gpu_percent'] - before_metrics['gpu_percent']:.1f}%")
                        with perf_col2:
                            st.metric("CPU Usage", f"{after_metrics['cpu_percent']:.1f}%",
                                      f"{after_metrics['cpu_percent'] - before_metrics['cpu_percent']:.1f}%")
                        with perf_col3:
                            if perf_metrics['last_inference_time'] > 0:
                                st.metric("Tokens/sec", f"{perf_metrics['tokens_per_second']:.1f}",
                                         f"{perf_metrics['model']}")
                            
            # Now analyze conversation using the existing vehicle_agent
            vehicle_mentions = vehicle_agent.analyze_conversation(st.session_state.conversation)
            if vehicle_mentions:
                with st.spinner("Searching CarMax..."):
                    search_result = vehicle_agent.search_vehicles(vehicle_mentions)
                    st.write(search_result)
                
    except Exception as e:
        st.error(f"Error Main Function: {str(e)}")
        
# 
if __name__ == "__main__":
    init_streamlit()  # Must be the first Streamlit command
    threading.Timer(2.0, open_chromium).start()
    main()