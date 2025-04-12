import streamlit as st
import time
import random
from datetime import datetime
import requests
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
import os
import glob
import PyPDF2
import docx
import fitz  # PyMuPDF for better PDF handling

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPWrapper:
    """Model Context Protocol wrapper for LLM interactions"""
    
    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/chat"
        
    def format_context(self, 
                       query: str, 
                       role: str, 
                       context: str = "", 
                       metadata: Dict[str, Any] = None) -> Dict:
        """Format query using MCP standards"""
        if not metadata:
            metadata = {}
            
        # Create MCP-formatted context
        return {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": f"You are acting as {role}. Respond according to your role and expertise."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuery: {query}"
                }
            ],
            "stream": False,
            "metadata": {
                "protocol_version": "mcp-v1",
                "timestamp": datetime.now().isoformat(),
                **metadata
            }
        }
    
    def query(self, 
              query: str, 
              role: str, 
              context: str = "", 
              metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute MCP-formatted query to the model"""
        if not metadata:
            metadata = {}
            
        mcp_request = self.format_context(query, role, context, metadata)
        response = None
        
        try:
            # Log the MCP request
            logger.info(f"MCP Request: {json.dumps(mcp_request, indent=2)[:200]}...")
            
            # Make the API call
            response = requests.post(
                self.api_url,
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Format as MCP response
            return {
                "success": True,
                "content": result["message"]["content"],
                "metadata": {
                    "protocol_version": "mcp-v1",
                    "model": self.model_name,
                    "timestamp": datetime.now().isoformat(),
                    **metadata
                }
            }
        except Exception as e:
            logger.error(f"MCP query error: {str(e)}")
            if response and hasattr(response, 'text'):
                logger.error(f"Response content: {response.text[:200]}...")
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "protocol_version": "mcp-v1",
                    "timestamp": datetime.now().isoformat()
                }
            }

class Agent:
    def __init__(self, name: str, role: str, expertise: List[str]):
        self.name = name
        self.role = role
        self.expertise = expertise
        self.conversation_history = []
        # Use MCP wrapper instead of direct Ollama calls
        self.mcp = MCPWrapper(model_name="llama3")
        
    def query_llm(self, prompt: str) -> str:
        """Query Ollama LLM using MCP wrapper"""
        # Format conversation history as context
        context = "\n".join([f"{msg['role']}: {msg['content']}" 
                          for msg in self.conversation_history[-5:]])
        
        # Add agent metadata for MCP
        metadata = {
            "agent": {
                "name": self.name,
                "role": self.role,
                "expertise": self.expertise
            },
            "conversation_turns": len(self.conversation_history)
        }
        
        # Query using MCP wrapper
        response = self.mcp.query(
            query=prompt,
            role=f"{self.name}, a {self.role}",
            context=context,
            metadata=metadata
        )
        
        # Handle response
        if response["success"]:
            return response["content"]
        else:
            return f"Error: {response.get('error', 'Unknown error')}"
            
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
            # Update status to "thinking"
            if 'agent_status' in st.session_state:
                st.session_state.agent_status[agent_id] = "thinking"
                st.session_state.status_placeholders[agent_id].markdown(
                    f"⏳ <span style='color:orange;'>Thinking</span>", unsafe_allow_html=True
                )
                # Create thinking animation effect
                time.sleep(0.5)  # Small delay to show status change
            
            # Update to responding
            if 'agent_status' in st.session_state:
                st.session_state.agent_status[agent_id] = "responding"
                st.session_state.status_placeholders[agent_id].markdown(
                    f"✏️ <span style='color:blue;'>Responding</span>", unsafe_allow_html=True
                )
            
            # Get the actual response
            response = agent.respond(query)
            responses[agent.name] = response
            
            # Update to complete
            if 'agent_status' in st.session_state:
                st.session_state.agent_status[agent_id] = "complete"
                st.session_state.status_placeholders[agent_id].markdown(
                    f"✅ <span style='color:green;'>Complete</span>", unsafe_allow_html=True
                )
        
        # Record in master history
        self.conversation_history.append({
            "query": query,
            "responses": responses,
            "timestamp": datetime.now().isoformat()
        })
        
        return responses

class DocumentProcessor:
    """Process and search local documents to provide context for MCP"""
    
    def __init__(self, documents_path: str = None):
        self.documents_path = documents_path or os.path.join(os.path.expanduser("~"), "Documents")
        self.document_index = {}
        self.supported_extensions = ['.pdf', '.txt', '.docx', '.md']
        self.initialized = False
        
    def initialize(self):
        """Scan and prepare document index"""
        st.toast("Indexing documents, please wait...")
        
        try:
            for ext in self.supported_extensions:
                files = glob.glob(os.path.join(self.documents_path, f"**/*{ext}"), recursive=True)
                for file_path in files:
                    self._process_file(file_path)
            
            self.initialized = True
            st.toast("Document indexing complete.")
        except Exception as e:
            logger.error(f"Error during document indexing: {str(e)}")
            st.toast("Error during document indexing.")

    def _process_file(self, file_path: str):
        """Process individual file and add to index"""
        try:
            file_extension = Path(file_path).suffix.lower()
            content = ""
            
            if file_extension == ".pdf":
                with fitz.open(file_path) as pdf:
                    for page in pdf:
                        content += page.get_text()
            elif file_extension == ".txt":
                with open(file_path, "r", encoding="utf-8") as txt_file:
                    content = txt_file.read()
            elif file_extension == ".docx":
                doc = docx.Document(file_path)
                content = "\n".join([para.text for para in doc.paragraphs])
            elif file_extension == ".md":
                with open(file_path, "r", encoding="utf-8") as md_file:
                    content = md_file.read()
            
            self.document_index[file_path] = content
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")

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
    
    # Initialize agent status tracking
    if 'agent_status' not in st.session_state:
        st.session_state.agent_status = {
            agent_id: "idle" for agent_id in st.session_state.master_agent.agents.keys()
        }
    
    # Add status animation placeholders
    if 'status_placeholders' not in st.session_state:
        st.session_state.status_placeholders = {}
    
    # Sidebar for agent information
    with st.sidebar:
        st.header("Active Agents")
        
        # Create status indicators for each agent
        for agent_id, agent in st.session_state.master_agent.agents.items():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"🤖 {agent.name}")
                st.write(f"Role: {agent.role}")
                expertise_text = ", ".join(agent.expertise[:2])
                if len(agent.expertise) > 2:
                    expertise_text += "..."
                st.caption(f"Expertise: {expertise_text}")
            
            with col2:
                # Create status indicator
                status = st.session_state.agent_status.get(agent_id, "idle")
                if status == "thinking":
                    st.markdown("⏳ <span style='color:orange;'>Thinking</span>", unsafe_allow_html=True)
                elif status == "responding":
                    st.markdown("✏️ <span style='color:blue;'>Responding</span>", unsafe_allow_html=True)
                elif status == "complete":
                    st.markdown("✅ <span style='color:green;'>Complete</span>", unsafe_allow_html=True)
                else:
                    st.markdown("💤 <span style='color:gray;'>Idle</span>", unsafe_allow_html=True)
                
                # Store placeholder for animation updates
                st.session_state.status_placeholders[agent_id] = st.empty()
            
            st.divider()
        
        # Add a reset button to clear statuses
        if st.button("Reset Agent Status"):
            for agent_id in st.session_state.agent_status:
                st.session_state.agent_status[agent_id] = "idle"
            st.rerun()
    
    # Main query input
    query = st.text_area("Enter your question:")
    if st.button("Ask Agents"):
        if query:
            # Reset agent statuses before starting
            for agent_id in st.session_state.agent_status:
                st.session_state.agent_status[agent_id] = "idle"
            
            with st.spinner("Agents are processing your query..."):
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