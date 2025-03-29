from time import sleep
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

# get config and create agents
todd, frank, conversation_starters = Agent.get_config()
    
for topic in conversation_starters:
    
    print(f"\nNew topic: {topic}")
    print("=" * 75)
    
    # Todd starts
    response = todd.respond(topic)
    print(f"Todd >>>>>: \n {response}")
    print("-" * 75)
    sleep(1)  # Add delay for readability
    
    # Frank responds to Todd
    response = frank.respond(f"Frank >>>>>: \n {response}")
    print(f"Frank >>>>>: {response}")
    print("-" * 75)

    sleep(1)
    
    # Todd responds to Frank
    response = todd.respond(f"Todd >>>>>: \n {response}")
    print(f"Todd: {response}")
    print("-" * 75)
    sleep(1)