import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import io

# OCR function
def extract_text_from_image(image_file):
    img = Image.open(image_file)
    text = pytesseract.image_to_string(img)
    return text

def extract_table_from_text(text):
    # Custom logic to extract only the table section
    lines = text.split('\n')
    table_lines = []
    start = False
    for line in lines:
        if 'Product description' in line or 'Gross Product Price' in line:
            start = True
        if start:
            table_lines.append(line)
            if 'Total Qty Purchased' in line:
                break
    return table_lines

st.title("Invoice Image to Table & Excel")

uploaded_file = st.file_uploader("Upload invoice image", type=["jpg", "png", "jpeg"])
if uploaded_file:
    text = extract_text_from_image(uploaded_file)
    st.text_area("Extracted Text", text, height=300)
    
    table_lines = extract_table_from_text(text)
    if table_lines:
        st.write("Item Table:")
        for line in table_lines:
            st.write(line)
        # (Parse lines into DataFrame for better copy/download)
    else:
        st.write("No item table found.")
