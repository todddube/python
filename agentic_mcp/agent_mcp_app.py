import streamlit as st
import time
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Optional
import json
from mcpclient import MCPClient
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentMCP:
    def __init__(self):
        self.mcp_client = MCPClient()
        self.agent_id = "demo_agent_1"
        self.knowledge_base = {}
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "llama2"
        self.initialize_storage()

    def initialize_storage(self):
        """Initialize storage for agent memory"""
        storage_dir = Path('agent_storage')
        storage_dir.mkdir(exist_ok=True)
        self.memory_file = storage_dir / 'agent_memory.json'
        
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                self.knowledge_base = json.load(f)
        else:
            self.save_memory()

    def save_memory(self):
        """Save agent memory to file"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.knowledge_base, f, indent=4)

    def query_llm(self, prompt: str) -> str:
        """Query Ollama LLM"""
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            logger.error(f"Error querying LLM: {str(e)}")
            return f"Error: {str(e)}"

    def analyze_knowledge(self, query: str) -> str:
        """Analyze knowledge base using LLM"""
        context = json.dumps(self.knowledge_base, indent=2)
        prompt = f"""Given this knowledge base:
{context}

Query: {query}

Please analyze the information and provide insights. Format your response in markdown."""
        
        return self.query_llm(prompt)

    def query_self(self) -> Dict:
        """Query own status and capabilities through MCP and analyze with LLM"""
        try:
            status = self.mcp_client.get_agent_status(self.agent_id)
            capabilities = self.mcp_client.get_agent_capabilities(self.agent_id)
            
            # Get LLM analysis
            analysis = self.query_llm(
                f"Analyze this agent status and capabilities:\n"
                f"Status: {status}\n"
                f"Capabilities: {capabilities}\n"
                f"What insights can you provide about this agent?"
            )
            
            return {
                "status": status,
                "capabilities": capabilities,
                "llm_analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error querying self: {str(e)}")
            return {"error": str(e)}

    def update_knowledge(self, key: str, value: any):
        """Update knowledge base with new information"""
        self.knowledge_base[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        self.save_memory()

    def get_knowledge(self, key: str) -> Optional[Dict]:
        """Retrieve information from knowledge base"""
        return self.knowledge_base.get(key)

def main():
    st.set_page_config(
        page_title="Agentic MCP Demo with LLM",
        page_icon="🤖",
        layout="wide"
    )

    st.title("🤖 Agentic MCP Demo with Llama2")
    st.write("Self-aware agent using MCP SDK and Ollama LLM")

    # Initialize agent
    if 'agent' not in st.session_state:
        st.session_state.agent = AgentMCP()
    
    # Sidebar controls
    with st.sidebar:
        st.header("Agent Controls")
        
        # LLM Analysis
        st.subheader("LLM Analysis")
        query = st.text_area("Ask about knowledge base:", height=100)
        if st.button("Analyze"):
            with st.spinner("Analyzing with Llama2..."):
                analysis = st.session_state.agent.analyze_knowledge(query)
                st.markdown(analysis)
        
        st.divider()
        
        if st.button("Query Self"):
            with st.spinner("Querying agent status..."):
                result = st.session_state.agent.query_self()
                st.session_state.agent.update_knowledge("last_self_query", result)

    # Main content area
    col1, col2 = st.columns(2)

    with col1:
        st.header("Agent Status")
        last_query = st.session_state.agent.get_knowledge("last_self_query")
        if last_query:
            st.json(last_query["value"])
            if "llm_analysis" in last_query["value"]:
                st.subheader("LLM Analysis")
                st.markdown(last_query["value"]["llm_analysis"])
        else:
            st.info("No self-query performed yet")