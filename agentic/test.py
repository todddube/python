from time import sleep
import streamlit as st
import requests
import pyhocon

def get_ollama_response(prompt, model="llama3"):
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
            config = pyhocon.ConfigFactory.parse_file(r'c:\\Users\\todd\\OneDrive\\Documents\\GitHub\\python\\agentic\\agents_config.hocon')
            
            # Create agents from config
            todd = Agent(
                name=config['agents.todd.name'],
                personality=config['agents.todd.personality']
            )

            frank = Agent(
                name=config['agents.frank.name'],
                personality=config['agents.frank.personality']
            )

            # Get conversation starters
            conversation_starters = config['conversation.starters']
            
            return todd, frank, conversation_starters
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
        
    # Add animated conversation visualization
    st.sidebar.markdown("### Conversation Status")
    cols = st.sidebar.columns([1, 1, 1])
    with cols[0]:
        st.markdown("Agent 🤖")
    with cols[1]:
        st.markdown("⚡")
    with cols[2]:
        st.markdown("Ollama 🤖")
    
    # Create animation container
    animation_container = st.sidebar.empty()
    
    # Simple animation frames
    frames = ["🔵   ⬜   ⬜",
             "⬜   🔵   ⬜", 
             "⬜   ⬜   🔵"]
    
    # Show animation frame
    current_frame = 0
    animation_container.markdown(frames[current_frame])
    sleep(0.1)  # Brief pause between frames

def main():
    init_streamlit()
        
    # Initialize session state
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
        
    # Get agents and topics
    try:
        todd, frank, conversation_starters = Agent.get_config()
        
        # Display current conversation starters in sidebar
        st.sidebar.markdown("### Available Topics")
        for starter in conversation_starters:
            st.sidebar.markdown(f"- {starter}")
        st.sidebar.markdown("---")
        
        # Display agents status in sidebar
        st.sidebar.markdown("### Agents Personality")
        st.sidebar.markdown(f"**Todd**: - {todd.personality}")
        st.sidebar.markdown(f"**Frank**: - {frank.personality}")
        st.sidebar.markdown("---")
        
        # Topic selector
        topic = st.selectbox("Select a conversation topic:", conversation_starters)
        
        if st.button("Start Conversation"):
            st.session_state.conversation = []  # Clear previous conversation
            
            # Display the topic
            st.subheader(f"Topic: {topic}")
            
            # Todd starts
            response = todd.respond(topic)
            st.session_state.conversation.append(("Todd", response))
            
            # Frank responds
            response = frank.respond(response)
            st.session_state.conversation.append(("Frank", response))
            
            # Todd responds again
            response = todd.respond(response)
            st.session_state.conversation.append(("Todd", response))
        
            # Display conversation
            for speaker, message in st.session_state.conversation:
                with st.container():
                    if speaker == "Todd":
                        st.markdown(f"**Todd**:")
                        st.markdown(f">{message}", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**Frank**:")
                        st.markdown(f">{message}", unsafe_allow_html=True)
                    st.markdown("---")
                
    except Exception as e:
        st.error(f"Error: {str(e)}")
            
if __name__ == "__main__":
    main()