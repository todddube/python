import streamlit as st
import time
from datetime import datetime
import requests
import json
from typing import Dict, List, Optional
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, name: str, role: str, expertise: List[str]):
        self.name = name
        self.role = role
        self.expertise = expertise
        self.conversation_history = []
        self.ollama_url = "http://localhost:11434/api/chat"
        
    def query_llm(self, prompt: str) -> str:
        """Query Ollama LLM"""
        response = None
        try:
            context = "\n".join([f"{msg['role']}: {msg['content']}" 
                               for msg in self.conversation_history[-5:]])
            
            full_prompt = f"""
            You are {self.name}, a {self.role} with expertise in {', '.join(self.expertise)}.
            Previous conversation:
            {context}
            
            Current query: {prompt}
            
            Respond in character, using your expertise to provide insights.
            """
            
            # Updated to use the /api/chat endpoint
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "llama3",
                    "messages": [
                        {
                            "role": "user", 
                            "content": full_prompt
                        }
                    ],
                    "stream": False
                },
                headers={"Content-Type": "application/json"}
            )
            
            # Proper error handling for response
            response.raise_for_status()
            
            # Safe JSON parsing
            try:
                result = response.json()
                return result['message']['content']
            except json.JSONDecodeError as json_err:
                logger.error(f"JSON decode error: {str(json_err)}")
                logger.error(f"Response content: {response.text[:200]}...")  # Log first 200 chars
                return f"Error parsing response: {str(json_err)}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to Ollama server. Is it running?"
        except Exception as e:
            logger.error(f"Error querying LLM: {str(e)}")
            if response and hasattr(response, 'text'):
                logger.error(f"Response text: {response.text[:200]}...")  # Log first 200 chars
            return f"Error: {str(e)}"
            
    def respond(self, query: str) -> str:
        """Generate a response to a query"""
        response = self.query_llm(query)
        self.conversation_history.append({
            "role": self.role,
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        return response

class MasterAgent:
    def __init__(self):
        self.agents = {
            "tech": Agent("TechBot", "Technical Expert", 
                         ["programming", "system architecture", "debugging"]),
            "creative": Agent("CreativeBot", "Creative Consultant", 
                            ["design", "user experience", "innovation"]),
            "analyst": Agent("AnalystBot", "Data Analyst", 
                           ["data analysis", "statistics", "research methods"])
        }
        self.conversation_history = []
        
    def coordinate_response(self, query: str) -> Dict:
        """Coordinate responses from all agents"""
        responses = {}
        
        for agent_id, agent in self.agents.items():
            responses[agent.name] = agent.respond(query)
            
        # Record in master history
        self.conversation_history.append({
            "query": query,
            "responses": responses,
            "timestamp": datetime.now().isoformat()
        })
        
        return responses

def main():
    st.set_page_config(
        page_title="Multi-Agent MCP Demo",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Multi-Agent MCP System")
    st.write("Ask a question and get responses from multiple AI agents")
    
    # Initialize master agent in session state
    if 'master_agent' not in st.session_state:
        st.session_state.master_agent = MasterAgent()
    
    # Sidebar for agent information
    with st.sidebar:
        st.header("Active Agents")
        for agent_id, agent in st.session_state.master_agent.agents.items():
            st.subheader(f"🤖 {agent.name}")
            st.write(f"Role: {agent.role}")
            st.write("Expertise:")
            for exp in agent.expertise:
                st.write(f"- {exp}")
            st.divider()
    
    # Main query input
    query = st.text_area("Enter your question:")
    if st.button("Ask Agents"):
        if query:
            with st.spinner("Agents are thinking..."):
                responses = st.session_state.master_agent.coordinate_response(query)
                
                # Display responses in columns
                cols = st.columns(len(responses))
                for i, (agent_name, response) in enumerate(responses.items()):
                    with cols[i]:
                        st.markdown(f"### {agent_name}")
                        st.markdown(response)
                        st.divider()
        else:
            st.warning("Please enter a question first!")
    
    # Conversation history
    if st.session_state.master_agent.conversation_history:
        st.header("Conversation History")
        for entry in reversed(st.session_state.master_agent.conversation_history):
            st.subheader(f"Query: {entry['query']}")
            st.caption(f"Time: {entry['timestamp']}")
            
            for agent_name, response in entry['responses'].items():
                with st.expander(f"{agent_name}'s Response"):
                    st.write(response)
            st.divider()

if __name__ == "__main__":
    main()