import streamlit as st
from PIL import Image
import ollama
import sys
import subprocess
from pathlib import Path

def get_llava_response(image_path, prompt):
    """Get response from LLaVA model via Ollama"""
    try:
        response = ollama.chat(
            model='llava',
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [image_path]
            }]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Configure Streamlit page
    st.set_page_config(
        page_title="LLaVA Image Analysis",
        page_icon="🖼️",
        layout="wide"
    )
    
    st.title("🖼️ Image Analysis with LLaVA")
    st.write("Upload an image to get an AI-powered description")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        
        # Button to analyze image
        if st.button("Describe Image"):
            prompt = "Please describe what you see in this image."
            
            # Save temporary file for Ollama
            temp_path = "temp_image.jpg"
            image.save(temp_path)
            
            # Get description from LLaVA
            with st.spinner('Analyzing image...'):
                description = get_llava_response(temp_path, prompt)
                st.write("Description:", description)

if __name__ == "__main__":
    try:
        # If running directly, start Streamlit
        if len(sys.argv) == 1:
            file_path = Path(__file__).absolute()
            subprocess.run([
                "streamlit", 
                "run", 
                str(file_path),
                "--server.port=8501",
                "--server.address=localhost"
            ], check=True)
        # If started by Streamlit, run the main function
        else:
            main()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)