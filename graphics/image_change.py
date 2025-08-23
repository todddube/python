import streamlit as st
from PIL import Image
import numpy as np

def pixelate(img, pixel_size=8):
    # Resize down
    small = img.resize(
        (img.width // pixel_size, img.height // pixel_size), Image.NEAREST
    )
    # Resize up
    result = small.resize(img.size, Image.NEAREST)
    return result

def quantize(img, colors=256):
    return img.convert('P', palette=Image.ADAPTIVE, colors=colors).convert('RGB')

def to_8bit_character(img):
    # Resize to small size for "character" look
    char_size = 32
    img = img.resize((char_size, char_size), Image.NEAREST)
    # Pixelate
    img = pixelate(img, pixel_size=4)
    # Reduce color palette
    img = quantize(img, colors=16)
    return img

st.title("8-bit Character Maker")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGBA")
    st.image(image, caption="Original Image", use_column_width=True)
    eight_bit_img = to_8bit_character(image)
    st.image(eight_bit_img, caption="8-bit Character", use_column_width=True)
    st.download_button(
        "Download 8-bit Image",
        data=eight_bit_img.tobytes(),
        file_name="8bit_character.png",
        mime="image/png"
    )