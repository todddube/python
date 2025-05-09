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

# Add version constants at top of file
__version__ = "0.1"
__author__ = "Todd Dube"

def open_ollama_logs_terminal():
    """Open a terminal window and tail Ollama logs."""
    try:
        # Create a logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        log_file = os.path.join(logs_dir, "ollama_logs.txt")
        
        # Create a batch file to run the continuous log fetching
        batch_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tail_ollama_logs.bat")
        with open(batch_file, "w") as f:
            f.write('@echo off\n')
            f.write(f'title Ollama Logs - {time()}\n')
            f.write('echo Tailing Ollama API logs...\n')
            f.write('echo Press Ctrl+C to stop\n')
            f.write('echo.\n')
            # Command to continuously poll the Ollama API and append to log file
            f.write(f':loop\n')
            f.write(f'powershell -command "try {{ Invoke-RestMethod -Uri http://localhost:11434/api/version }} catch {{ \\"Ollama API Error: $_\\" }}" >> "{log_file}"\n')
            f.write(f'powershell -command "try {{ Invoke-RestMethod -Uri http://localhost:11434/api/tags }} catch {{ \\"Ollama Tags Error: $_\\" }}" >> "{log_file}"\n')
            f.write(f'type "{log_file}"\n')
            f.write('timeout /t 5 /nobreak > nul\n')
            f.write('cls\n')
            f.write('goto loop\n')
        
        # Open the batch file in a new command prompt window
        subprocess.Popen(f'start cmd.exe /k "{batch_file}"', shell=True)
        print(f"Ollama logs terminal opened. Logs saved to: {log_file}")
        return True
    except Exception as e:
        print(f"Error opening Ollama logs terminal: {str(e)}")
        return False

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

def get_ollama_response(prompt, model="llama3"):
    start_time = time()
    try:
        response = requests.post('http://localhost:11434/api/generate',
                               json={
                                   "model": model,
                                   "prompt": prompt,
                                   "system": "",
                                   "stream": False,
                                   "temperature": 0.7
                               })
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        json_response = response.json()
        
        # Update sidebar with query info
        # with st.sidebar.expander("🔄 Recent Activity", expanded=True):
        #     st.write(f"Query sent: {prompt[:50]}...")
        #     st.write(f"Response time: {time() - start_time:.2f} seconds")
            
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

    def __getattr__(self, name):
        # Handle missing attributes gracefully
        if name in self.__dict__:
            return self.__dict__[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def respond(self, message):
        context = f"""
        You are {self.name}. {self.personality}
        Previous conversation: {self.conversation_history}
        Respond to: {message}
        Keep response brief and in character.
        """
        response = get_ollama_response(context)
        self.conversation_history.append(f"{self.name}: {response}")
        return response

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
    """Check if the Ollama service is running."""
    
    # Add status check for Ollama service
    try:
        response = requests.get('http://localhost:11434/api/version')
        if response.status_code == 200:
            st.sidebar.markdown("""
                <style>
                @keyframes flashingColors {
                    0% { color: #FF0000; }
                    25% { color: #00FF00; }
                    50% { color: #0000FF; }
                    75% { color: #FFFF00; }
                    100% { color: #FF0000; }
                }
                .flashing-text {
                    animation: flashingColors 2s infinite;
                    font-weight: bold;
                }
                </style>
                <span class="flashing-text">🟢 Ollama service is running</span>
            """, unsafe_allow_html=True)
        else:
            st.sidebar.error("🔴 Ollama service is not responding properly")
            st.error("Ollama service is not responding properly. Please check if it's running correctly.")
            
    except requests.exceptions.RequestException:
        st.sidebar.error("🔴 Ollama service is not running")

    # Check model availability
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            models = response.json()
            st.sidebar.write("Available Models:")
            for model in models['models']:
                st.sidebar.write(f"- {model['name']}")
    except requests.exceptions.RequestException:
        st.sidebar.warning("⚠️ Cannot fetch available models")


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
        
        if st.button("Start Conversation"):
            # Create vehicle agent first, before starting conversation
            vehicle_agent = VehicleAgent()
            
            st.session_state.conversation = []  # Clear previous conversation
            st.subheader(f"Topic: {topic}")
            
            # Create placeholder for conversation
            conversation_placeholder = st.empty()
         
            # Iterate the specified number of times
            for _ in range(num_iterations):
                for agent in agents:
                    with st.spinner(f"Waiting for {agent.name}'s response..."):
                        response = agent.respond(topic)
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
    open_ollama_logs_terminal()  # Open Ollama logs terminal on startup
    threading.Timer(2.0, open_chromium).start()
    main()