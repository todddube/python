import os
import streamlit as st
import ollama
import time
import glob
import tempfile
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import json
import asyncio
from datetime import datetime
from langchain_community.document_loaders import (
    TextLoader, 
    PDFMinerLoader,
    CSVLoader,
    Docx2txtLoader,
    UnstructuredExcelLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama

# Configure logging
log_directory = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_directory, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_directory, "documents_log.txt")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DocumentIndexer")

# MCP Server Configuration
class MCPServer:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name
        self.embeddings = None
        self.vector_store = None
        self.qa_chain = None
        self.documents_indexed = 0
        self.status = "Not Started"
        self.is_running = False
        
    def initialize_embeddings(self):
        """Initialize the embeddings model from Ollama"""
        try:
            self.embeddings = OllamaEmbeddings(model=self.model_name)
            return True
        except Exception as e:
            logger.error(f"Error initializing embeddings: {str(e)}")
            return False
    
    def get_loader_for_file(self, file_path: str):
        """Get the appropriate document loader based on file extension"""
        ext = file_path.lower().split('.')[-1]
        try:
            if ext == 'txt' or ext == 'md' or ext == 'py' or ext == 'js' or ext == 'html' or ext == 'css':
                return TextLoader(file_path, encoding='utf-8', autodetect_encoding=True)
            elif ext == 'pdf':
                return PDFMinerLoader(file_path)
            elif ext == 'csv':
                return CSVLoader(file_path)
            elif ext == 'docx':
                return Docx2txtLoader(file_path)
            elif ext == 'xlsx' or ext == 'xls':
                return UnstructuredExcelLoader(file_path)
            else:
                logger.warning(f"Unsupported file format: {ext} for file {file_path}")
                return None
        except Exception as e:
            logger.error(f"Error getting loader for {file_path}: {str(e)}")
            return None

    def index_files(self, directory_path: str):
        """Index all files in the given directory recursively"""
        self.status = "Indexing"
        self.is_running = True
        
        # Initialize embeddings
        if not self.initialize_embeddings():
            self.status = "Failed - Embeddings initialization error"
            self.is_running = False
            return False
        
        # Get all files recursively
        try:
            all_files = []
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    all_files.append(file_path)
            
            # Process the files
            documents = []
            for file_path in all_files:
                try:
                    loader = self.get_loader_for_file(file_path)
                    if loader:
                        file_docs = loader.load()
                        if file_docs:
                            documents.extend(file_docs)
                            self.documents_indexed += 1
                            logger.info(f"Indexed: {file_path}")
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {str(e)}")
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100,
            )
            split_docs = text_splitter.split_documents(documents)
            
            # Create vector store
            if split_docs:
                self.vector_store = FAISS.from_documents(
                    split_docs, 
                    self.embeddings
                )
                
                # Create QA chain
                self.qa_chain = RetrievalQA.from_chain_type(
                    llm=Ollama(model=self.model_name, callbacks=[StreamingStdOutCallbackHandler()]),
                    chain_type="stuff",
                    retriever=self.vector_store.as_retriever(),
                    return_source_documents=True
                )
                
                self.status = f"Ready - Indexed {self.documents_indexed} files"
                logger.info(f"Completed indexing {self.documents_indexed} files")
            else:
                self.status = "No documents indexed"
                logger.warning("No documents were indexed")
            
            self.is_running = False
            return True
            
        except Exception as e:
            logger.error(f"Error during indexing process: {str(e)}")
            self.status = f"Error - {str(e)}"
            self.is_running = False
            return False
    
    def ask(self, query: str) -> Dict[str, Any]:
        """Query the indexed documents"""
        if not self.qa_chain:
            return {"answer": "No documents have been indexed yet.", "sources": []}
        
        try:
            result = self.qa_chain({"query": query})
            sources = []
            if "source_documents" in result:
                for doc in result["source_documents"]:
                    if hasattr(doc, "metadata") and "source" in doc.metadata:
                        sources.append(doc.metadata["source"])
            
            return {
                "answer": result["result"],
                "sources": list(set(sources))  # Remove duplicates
            }
        except Exception as e:
            logger.error(f"Error querying documents: {str(e)}")
            return {"answer": f"Error: {str(e)}", "sources": []}

# Streamlit UI
st.set_page_config(
    page_title="OneDrive Documents Indexer",
    page_icon="📚",
    layout="wide"
)

# Initialize server instance in session state if not already present
if 'mcp_server' not in st.session_state:
    st.session_state.mcp_server = MCPServer()

if 'indexing_thread' not in st.session_state:
    st.session_state.indexing_thread = None

mcp_server = st.session_state.mcp_server

st.title("OneDrive Documents Indexer")
st.write("Index and search all documents in your OneDrive Documents folder using Ollama's llama3 model")

# Get OneDrive Documents path
onedrive_path = os.path.expanduser("~/OneDrive/Documents")

with st.sidebar:
    st.subheader("Settings")
    
    # Model selection
    model_options = ["llama3", "llama3:latest", "mistral", "phi3"]
    selected_model = st.selectbox("Select Ollama Model", model_options, index=0)
    
    # Index button
    if st.button("Start Indexing"):
        if not mcp_server.is_running:
            mcp_server.model_name = selected_model
            
            # Create a progress message
            progress_placeholder = st.empty()
            progress_placeholder.info("Starting indexing process...")
            
            # Start indexing in a separate thread to keep UI responsive
            import threading
            
            def index_documents():
                try:
                    mcp_server.index_files(onedrive_path)
                except Exception as e:
                    logger.error(f"Error in indexing thread: {str(e)}")
                
            st.session_state.indexing_thread = threading.Thread(target=index_documents)
            st.session_state.indexing_thread.start()
    
    # Show indexing status
    st.subheader("Status")
    status_placeholder = st.empty()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Query input
    query = st.text_area("Ask a question about your documents", height=100)
    if st.button("Search"):
        if mcp_server.vector_store is not None:
            with st.spinner("Searching documents..."):
                result = mcp_server.ask(query)
                st.subheader("Answer")
                st.write(result["answer"])
                
                if result["sources"]:
                    st.subheader("Sources")
                    for source in result["sources"]:
                        st.write(f"- {source}")
        else:
            st.error("Please index your documents first")

with col2:
    # Files indexed information
    st.subheader("Indexing Statistics")
    st.metric("Files Indexed", mcp_server.documents_indexed)
    
    # Update status in sidebar
    if mcp_server.is_running:
        status_placeholder.info(f"Status: {mcp_server.status}")
    elif mcp_server.documents_indexed > 0:
        status_placeholder.success(f"Status: {mcp_server.status}")
    else:
        status_placeholder.info("Status: Not started")

# Footer
st.markdown("---")
st.caption("Built with Streamlit and Ollama LLM")

# Main app execution
def main():
    # This function is a placeholder for future functionality if needed
    pass

if __name__ == "__main__":
    main()