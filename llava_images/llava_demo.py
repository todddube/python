import streamlit as st
from PIL import Image
import ollama
import sys
import subprocess
from pathlib import Path
import os
import time

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

def get_llava_response(image_path: str, prompt: str) -> dict:
    """Get response from LLaVA model via Ollama with error handling"""
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

def main():
    # Sidebar configuration
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/ollama/ollama/main/docs/ollama.png", width=100)
        st.title("LLaVA Vision")
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
        # Create two columns for image and analysis
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Uploaded Image")
            image = Image.open(uploaded_file)
            st.image(image, caption='', use_column_width=True, clamp=True)
        
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
    try:
        if len(sys.argv) == 1:
            file_path = Path(__file__).absolute()
            subprocess.run([
                "streamlit", 
                "run", 
                str(file_path),
                "--server.port=8501",
                "--server.address=localhost",
                "--theme.primaryColor=#FF4B4B",
                "--theme.backgroundColor=#FFFFFF",
                "--theme.secondaryBackgroundColor=#F0F2F6",
                "--theme.textColor=#262730"
            ], check=True)
        else:
            main()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)