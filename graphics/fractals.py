import streamlit as st
import numpy as np
from PIL import Image
import random
import colorsys

# Configure page
st.set_page_config(
    page_title="Fractal Generator",
    page_icon="🔮",
    layout="wide"
)

# Existing mandelbrot function
def mandelbrot(h, w, max_iter, random_params=True):
    if random_params:
        x_min, x_max = -2 + random.uniform(-0.5, 0.5), 0.5 + random.uniform(-0.2, 0.2)
        y_min, y_max = -1.5 + random.uniform(-0.3, 0.3), 1.5 + random.uniform(-0.3, 0.3)
    else:
        x_min, x_max = -2, 0.5
        y_min, y_max = -1.5, 1.5
        
    x, y = np.linspace(x_min, x_max, w), np.linspace(y_min, y_max, h)
    X, Y = np.meshgrid(x, y)
    Z = X + Y*1j
    C = Z.copy()
    divtime = max_iter + np.zeros(Z.shape, dtype=int)
    
    for i in range(max_iter):
        Z = Z**2 + C
        diverge = Z*np.conj(Z) > 2**2
        div_now = diverge & (divtime == max_iter)
        divtime[div_now] = i
        Z[diverge] = 2
    
    return divtime

# Existing julia function
def julia(h, w, max_iter, c):
    x = np.linspace(-2, 2, w)
    y = np.linspace(-2, 2, h)
    X, Y = np.meshgrid(x, y)
    Z = X + Y*1j
    divtime = max_iter + np.zeros(Z.shape, dtype=int)
    
    for i in range(max_iter):
        Z = Z**2 + c
        diverge = Z*np.conj(Z) > 2**2
        div_now = diverge & (divtime == max_iter)
        divtime[div_now] = i
        Z[diverge] = 2
    
    return divtime

def create_colormap(max_iter):
    colors = []
    for i in range(max_iter):
        hue = (i / max_iter + random.uniform(-0.1, 0.1)) % 1.0
        saturation = random.uniform(0.8, 1.0)
        value = random.uniform(0.8, 1.0)
        rgb = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(hue, saturation, value))
        colors.append(rgb)
    colors.append((0, 0, 0))
    return colors

# Sidebar
st.sidebar.title("Controls")
fractal_choice = st.sidebar.radio(
    "Choose Fractal Type",
    ["Random", "Mandelbrot", "Julia"]
)

max_iter = st.sidebar.slider("Max Iterations", 50, 200, 100)
width = st.sidebar.slider("Width", 400, 1200, 800)
height = st.sidebar.slider("Height", 300, 900, 600)

st.sidebar.markdown("""
## About
This app generates beautiful fractals using:
- Mandelbrot Set
- Julia Set

Adjust the parameters in the sidebar and click 'Generate' to create!
""")

# Main content
st.title("🔮 Fractal Generator")

if st.button("Generate New Fractal"):
    with st.spinner("Generating fractal..."):
        try:
            if fractal_choice == "Random":
                fractal_type = random.choice(["mandelbrot", "julia"])
            else:
                fractal_type = fractal_choice.lower()
                
            if fractal_type == "mandelbrot":
                fractal = mandelbrot(height, width, max_iter, random_params=True)
                st.write("✨ Generated a Mandelbrot Set")
            else:
                c = complex(random.uniform(-1, 1), random.uniform(-1, 1))
                fractal = julia(height, width, max_iter, c)
                st.write(f"✨ Generated a Julia Set with c = {c:.2f}")
            
            colors = create_colormap(max_iter)
            img = Image.new('RGB', (width, height))
            pixels = img.load()
            
            for i in range(width):
                for j in range(height):
                    pixels[i, j] = colors[fractal[j, i]]
            
            st.image(img, use_container_width=True)
            st.caption(f"Using {max_iter} iterations | Image size: {width}x{height}")
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            
# Add footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")