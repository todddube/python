import streamlit as st
from PIL import Image
import ollama
import sys
import subprocess
from pathlib import Path
import os
import time
import requests

# Configure page and styling
st.set_page_config(
    page_title="LLaVA Vision Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #FF4B4B;
    }
    .uploadedImage {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

def check_ollama_server() -> tuple[bool, str]:
    """Check if Ollama server is running and LLaVA model is available"""
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            models = [model['name'] for model in response.json()['models']]
            if 'llava' in models:
                return True, "Server running and LLaVA model available"
            else:
                return False, "LLaVA model not found. Please run: ollama pull llava"
        return False, "Ollama server not responding correctly"
    except requests.exceptions.ConnectionError:
        return False, "Ollama server not running. Please start with: ollama serve"
    except Exception as e:
        return False, f"Error checking Ollama server: {str(e)}"

def get_llava_response(image_path: str, prompt: str) -> dict:
    """Get response from LLaVA model via Ollama with error handling"""
    # Check server status first
    server_ok, error_msg = check_ollama_server()
    if not server_ok:
        return {"success": False, "error": error_msg}
        
    try:
        with st.spinner('🤖 AI is analyzing your image...'):
            response = ollama.chat(
                model='llava',
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [image_path]
                }]
            )
            return {"success": True, "content": response['message']['content']}
    except Exception as e:
        return {"success": False, "error": str(e)}

def save_upload_file_tmp(uploadedfile):
    """Save uploaded file to temporary directory"""
    tmp_dir = Path("temp_uploads")
    tmp_dir.mkdir(exist_ok=True)
    
    temp_file = tmp_dir / f"upload_{int(time.time())}.jpg"
    with open(temp_file, "wb") as f:
        f.write(uploadedfile.getbuffer())
    return str(temp_file)

def validate_image(file) -> tuple[bool, str]:
    """Validate uploaded image file"""
    # Check file size (10MB limit)
    MAX_SIZE = 10 * 1024 * 1024  # 10MB
    if file.size > MAX_SIZE:
        return False, "File size too large. Please upload images under 10MB."
    
    try:
        # Try to open and verify image
        image = Image.open(file)
        image.verify()
        # Rewind file pointer after verify
        file.seek(0)
        return True, ""
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"

def main():
    # Sidebar configuration
    with st.sidebar:
        st.title("LLaVA Vision")
        server_ok, status_msg = check_ollama_server()
        status_color = "green" if server_ok else "red"
        st.markdown(f"Server Status: <span style='color:{status_color}'>{status_msg}</span>", 
                   unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("""
        ### About
        This app uses LLaVA (Large Language and Vision Assistant) 
        to analyze images and provide detailed descriptions.
        
        ### Features
        - 🖼️ Image Analysis
        - 📝 Detailed Descriptions
        - 🤖 AI-Powered Insights
        """)
        
        # Custom prompt input
        st.markdown("### Custom Prompt")
        custom_prompt = st.text_area(
            "Customize your question about the image:",
            "Please describe what you see in this image.",
            help="You can ask specific questions about the image"
        )

    # Main content
    st.title("🤖 LLaVA Vision Assistant")
    st.markdown("### Upload an image for AI analysis")
    
    # File uploader with preview
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg'],
        help="Supported formats: JPG, JPEG, PNG"
    )
    
    if uploaded_file is not None:
        # Validate image first
        is_valid, error_msg = validate_image(uploaded_file)
        
        if not is_valid:
            st.error(error_msg)
        else:
            # Create two columns for image and analysis
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### Uploaded Image")
                try:
                    image = Image.open(uploaded_file)
                    st.image(image, caption='', use_column_width=True, clamp=True)
                except Exception as e:
                    st.error(f"Error displaying image: {str(e)}")
                    return
            
            with col2:
                st.markdown("### AI Analysis")
                if st.button("🔍 Analyze Image", key="analyze"):
                    # Save and analyze image
                    temp_path = save_upload_file_tmp(uploaded_file)
                    
                    # Get AI response
                    result = get_llava_response(temp_path, custom_prompt)
                    
                    if result["success"]:
                        st.markdown("#### AI Insights:")
                        st.markdown(f">{result['content']}")
                        
                        # Add confidence disclaimer
                        st.markdown("---")
                        st.caption(
                            "Note: AI analysis is based on probabilities and may not be 100% accurate."
                        )
                    else:
                        st.error(f"Error analyzing image: {result['error']}")
                    
                    # Cleanup temporary file
                    try:
                        os.remove(temp_path)
                    except:
                        pass

if __name__ == "__main__":
    main()