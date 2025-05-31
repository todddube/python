import os
import streamlit as st
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader, CSVLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
import tempfile
import time

# Set page configuration
st.set_page_config(
    page_title="Local Document Search with Ollama",
    page_icon="🔍",
    layout="wide",
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    .stButton>button {
        width: 100%;
    }
    .status {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success {
        background-color: rgba(0, 255, 0, 0.1);
        border: 1px solid green;
    }
    .loading {
        background-color: rgba(255, 255, 0, 0.1);
        border: 1px solid orange;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "initialized" not in st.session_state:
    st.session_state.initialized = False
    st.session_state.index_status = None
    st.session_state.vector_store = None
    st.session_state.ollama_model = "llama3"  # default model
    st.session_state.indexed_paths = []
    st.session_state.document_count = 0
    st.session_state.chat_history = []

def create_retrieval_qa_chain(vector_store, model_name):
    """Create a retrieval QA chain using the vector store and Ollama model."""
    try:
        llm = Ollama(model=model_name)
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            verbose=False
        )
        return qa_chain
    except Exception as e:
        st.error(f"Error setting up Ollama model: {e}")
        st.error("Make sure Ollama is running locally with your selected model.")
        return None

def load_documents(directory_path, extensions):
    """Load documents from a directory with specific extensions."""
    st.session_state.index_status = "Loading documents..."
    
    loaders = []
    document_counts = {}
    
    # Create a loader for each supported file type
    if extensions["txt"]:
        txt_loader = DirectoryLoader(
            directory_path, 
            glob="**/*.txt",
            loader_cls=TextLoader,
            show_progress=True,
            use_multithreading=True
        )
        loaders.append(("Text files (.txt)", txt_loader))
        
    if extensions["pdf"]:
        pdf_loader = DirectoryLoader(
            directory_path, 
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True,
            use_multithreading=True
        )
        loaders.append(("PDF documents (.pdf)", pdf_loader))
        
    if extensions["csv"]:
        csv_loader = DirectoryLoader(
            directory_path, 
            glob="**/*.csv",
            loader_cls=CSVLoader,
            show_progress=True,
            use_multithreading=True
        )
        loaders.append(("CSV files (.csv)", csv_loader))
        
    if extensions["docx"]:
        docx_loader = DirectoryLoader(
            directory_path, 
            glob="**/*.docx",
            loader_cls=Docx2txtLoader,
            show_progress=True,
            use_multithreading=True
        )
        loaders.append(("Word documents (.docx)", docx_loader))
    
    # Load each document type and count them
    all_documents = []
    for doc_type, loader in loaders:
        with st.spinner(f"Loading {doc_type}..."):
            try:
                docs = loader.load()
                document_counts[doc_type] = len(docs)
                all_documents.extend(docs)
                st.session_state.index_status = f"Loaded {len(docs)} {doc_type}..."
            except Exception as e:
                st.warning(f"Error loading {doc_type}: {str(e)}")
                document_counts[doc_type] = 0
    
    return all_documents, document_counts

def process_documents(documents):
    """Process and split documents for indexing."""
    st.session_state.index_status = f"Processing {len(documents)} documents..."
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    
    # Split documents into chunks
    chunks = text_splitter.split_documents(documents)
    
    st.session_state.index_status = f"Created {len(chunks)} chunks from {len(documents)} documents..."
    return chunks

def create_vector_index(chunks):
    """Create a vector index from document chunks."""
    st.session_state.index_status = f"Creating vector index from {len(chunks)} chunks..."
    
    # Use HuggingFaceEmbeddings as a local embedder
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    # Create FAISS index
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    st.session_state.index_status = "Vector index created successfully!"
    return vector_store

def main():
    st.title("🔍 Local Document Search with Ollama")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Ollama model selection
        st.subheader("Ollama Model")
        model_options = ["llama3", "llama2", "mistral", "gemma", "phi", "codellama"]
        selected_model = st.selectbox(
            "Select Ollama model",
            options=model_options,
            index=model_options.index(st.session_state.ollama_model),
            help="Select the model that you have available locally in Ollama"
        )
        st.session_state.ollama_model = selected_model
        
        st.divider()
        
        # Document indexing section
        st.subheader("Document Indexing")
        directory_path = st.text_input("Directory Path to Index:", placeholder="C:/Users/YourName/Documents")
        
        # File type selection
        st.write("Select file types to index:")
        col1, col2 = st.columns(2)
        with col1:
            include_txt = st.checkbox("Text (.txt)", value=True)
            include_pdf = st.checkbox("PDF (.pdf)", value=True)
        with col2:
            include_csv = st.checkbox("CSV (.csv)", value=True)
            include_docx = st.checkbox("Word (.docx)", value=True)
            
        extensions = {
            "txt": include_txt,
            "pdf": include_pdf,
            "csv": include_csv,
            "docx": include_docx
        }
        
        # Index button
        if st.button("Build Search Index"):
            if not directory_path or not os.path.isdir(directory_path):
                st.error("Please enter a valid directory path.")
            elif not any(extensions.values()):
                st.error("Please select at least one file type.")
            else:
                with st.spinner("Building index..."):
                    # Reset the current index
                    st.session_state.vector_store = None
                    st.session_state.initialized = False
                    
                    # Load and process documents
                    try:
                        documents, doc_counts = load_documents(directory_path, extensions)
                        
                        if documents:
                            # Store document counts for display
                            st.session_state.document_count = len(documents)
                            st.session_state.doc_counts = doc_counts
                            
                            # Process documents
                            chunks = process_documents(documents)
                            
                            # Create vector index
                            vector_store = create_vector_index(chunks)
                            
                            # Store in session state
                            st.session_state.vector_store = vector_store
                            st.session_state.initialized = True
                            st.session_state.indexed_paths.append(directory_path)
                            
                            st.success(f"Successfully indexed {len(documents)} documents from {directory_path}")
                        else:
                            st.warning("No documents found in the specified directory with the selected file types.")
                    except Exception as e:
                        st.error(f"Error building index: {str(e)}")
        
        # Display indexing status if active
        if st.session_state.index_status:
            status_container = st.empty()
            status_html = f"""<div class="status {'success' if 'success' in st.session_state.index_status.lower() else 'loading'}">
                            {st.session_state.index_status}</div>"""
            status_container.markdown(status_html, unsafe_allow_html=True)
        
        st.divider()
        
        # About section
        with st.expander("About"):
            st.markdown("""
            This app creates a search index from your local documents and allows you to query them using Ollama.
            
            **Requirements:**
            - [Ollama](https://ollama.ai/) installed and running locally
            - Selected model pulled in Ollama (run `ollama pull modelname`)
            
            **Features:**
            - Index multiple document types (PDF, TXT, DOCX, CSV)
            - Fast local search with FAISS
            - Query documents with Ollama LLMs
            - Document sources shown with responses
            """)
    
    # Main content area
    if not st.session_state.initialized:
        # Welcome message for first-time users
        st.info("👋 Welcome! Please use the sidebar to select a directory and build a search index.")
        
        # Placeholder welcome content
        st.markdown("""
        ## How it works
        
        1. **Select an Ollama model** from the sidebar (make sure it's installed locally)
        2. **Choose a directory** containing your documents to index
        3. **Select file types** you want to include in your search
        4. **Click "Build Search Index"** to create a searchable index
        5. **Ask questions** about your documents in the search box below
        
        The app will search through your documents and provide relevant answers using the Ollama model you selected.
        """)
    else:
        # Display information about the current index
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Current Index")
            st.write(f"📁 Directories indexed: {len(st.session_state.indexed_paths)}")
            st.write(f"📄 Total documents: {st.session_state.document_count}")
        
        with col2:
            st.subheader("Documents by Type")
            for doc_type, count in st.session_state.doc_counts.items():
                if count > 0:
                    st.write(f"- {doc_type}: {count}")
        
        st.divider()
        
        # Search interface
        st.subheader("Ask Questions About Your Documents")
        query = st.text_input("Enter your question:", placeholder="What information can I find in these documents?")
        
        if query:
            try:
                # Create QA chain if needed
                qa_chain = create_retrieval_qa_chain(st.session_state.vector_store, st.session_state.ollama_model)
                
                if qa_chain:
                    with st.spinner(f"Searching and generating response with {st.session_state.ollama_model}..."):
                        # Get the response from the chain
                        start_time = time.time()
                        result = qa_chain({"query": query})
                        end_time = time.time()
                        
                        # Extract answer and source documents
                        answer = result.get("result", "No answer generated")
                        source_docs = result.get("source_documents", [])
                        
                        # Display the answer
                        st.markdown("### Answer")
                        st.markdown(answer)
                        
                        # Display sources
                        if source_docs:
                            with st.expander(f"Sources ({len(source_docs)})", expanded=False):
                                for i, doc in enumerate(source_docs):
                                    st.markdown(f"**Source {i+1}**")
                                    st.markdown(f"**Path:** {doc.metadata.get('source', 'Unknown')}")
                                    st.markdown("**Content:**")
                                    st.markdown(f"```\n{doc.page_content[:300]}{'...' if len(doc.page_content) > 300 else ''}\n```")
                                    st.divider()
                        
                        # Display performance metrics
                        st.caption(f"⏱️ Response generated in {end_time - start_time:.2f} seconds")
                        
                        # Add to chat history
                        st.session_state.chat_history.append({
                            "question": query,
                            "answer": answer,
                            "sources": [doc.metadata.get('source', 'Unknown') for doc in source_docs[:3]]
                        })
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
        
        # Show chat history
        if st.session_state.chat_history:
            st.divider()
            st.subheader("Recent Questions")
            for i, chat in enumerate(st.session_state.chat_history[-5:]):  # Show last 5 exchanges
                with st.expander(f"Q: {chat['question']}", expanded=False):
                    st.markdown(chat["answer"])
                    if chat["sources"]:
                        st.caption(f"Sources: {', '.join([os.path.basename(s) for s in chat['sources']])}")

if __name__ == "__main__":
    main()