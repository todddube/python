from time import sleep
from time import time
import webbrowser
import os
import subprocess
import streamlit as st
import requests
import pyhocon


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
        with st.sidebar.expander("🔄 Recent Activity", expanded=True):
            st.write(f"Query sent: {prompt[:100]}...")
            st.write(f"Response time: {time() - start_time:.2f} seconds")
            #st.write(f"Epochs: {time():.0f}")
            
        if 'response' in json_response:
            return json_response['response']
        else:
            raise KeyError("Key 'response' not found in the API response.")

    except requests.exceptions.RequestException as e:
        return f"Error: Failed to connect to the API. {e}"
    except KeyError as e:
        return f"Error: {e}"

class Agent:
    """Agents class defining agent name and personality."""
    def __init__(self, name, personality):
        self.name = name
        self.personality = personality
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
                    personality=agent_config['personality']
                )
                agents.append(agent)

            # Get conversation starters
            conversation_starters = config['conversation.starters']
            
            return agents, conversation_starters
        except Exception as e:
            raise Exception(f"Error loading configuration: {e}")
        
def init_streamlit():
    """Initialize Streamlit configuration and check services."""
    # Configure Streamlit theme
    st.set_page_config(
        page_title="Agentic Conversation Simulator",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    # Add status check for Ollama service
    try:
        response = requests.get('http://localhost:11434/api/version')
        if response.status_code == 200:
            st.sidebar.success("🟢 Ollama service is running")
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
    init_streamlit()
        
    # Initialize session state
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
        
    # Get agents and topics
    try:
        agents, conversation_starters = Agent.get_config()
        
        # Display agents status in sidebar
        st.sidebar.markdown("### Agents & Personality")
        for agent in agents:
            st.sidebar.markdown(f"**{agent.name}**: {agent.personality}")
        st.sidebar.markdown("---")
        
        # Display current conversation starters in sidebar
        st.sidebar.markdown("### Available Topics")
        for starter in conversation_starters:
            st.sidebar.markdown(f"- {starter}")
        st.sidebar.markdown("---")
        
        # Topic selector
        topic = st.selectbox("Select a conversation topic:", conversation_starters)
        
        if st.button("Start Conversation"):
            st.session_state.conversation = []  # Clear previous conversation
            # Display the topic
            st.subheader(f"Topic: {topic}")
            
            # Create placeholder for conversation
            conversation_placeholder = st.empty()
            
            # toddai starts
            with st.spinner("toddai is thinking..."):
                response = toddai.respond(topic)
                st.session_state.conversation.append(("toddai", response))
                # Update display
                with conversation_placeholder.container():
                    for speaker, msg in st.session_state.conversation:
                        st.markdown(f"**{speaker}**:")
                        st.markdown(f">{msg}", unsafe_allow_html=True)
                        st.markdown("---")
            
            # frankai responds
            with st.spinner("frankai is thinking..."):
                response = frankai.respond(response)
                st.session_state.conversation.append(("frankai", response))
                # Update display
                with conversation_placeholder.container():
                    for speaker, msg in st.session_state.conversation:
                        st.markdown(f"**{speaker}**:")
                        st.markdown(f">{msg}", unsafe_allow_html=True)
                        st.markdown("---")
            
            # toddai responds again
            with st.spinner("toddai is thinking..."):
                response = toddai.respond(response)
                st.session_state.conversation.append(("toddai", response))
                # Update display
                with conversation_placeholder.container():
                    for speaker, msg in st.session_state.conversation:
                        st.markdown(f"**{speaker}**:")
                        st.markdown(f">{msg}", unsafe_allow_html=True)
                        st.markdown("---")

    except Exception as e:
        st.error(f"Error: {str(e)}")
            
if __name__ == "__main__":
    import threading
    threading.Timer(2.0, open_chromium).start()  # Delay to allow Streamlit to start
    
    main()