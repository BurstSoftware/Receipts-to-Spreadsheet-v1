import streamlit as st
from PIL import Image
import pytesseract
import io
import re
import pandas as pd
from datetime import datetime

# Explicitly set the tesseract command path
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def process_receipt_image(image):
    """
    Process the receipt image using OCR and extract relevant information
    """
    # Convert the image to text using pytesseract
    text = pytesseract.image_to_string(image)
    
    # Parse the text to extract line items
    lines = text.split('\n')
    items = []
    
    # Basic parsing logic - can be enhanced based on receipt format
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
            
        # Look for price patterns
        price_pattern = r'\$?\d+\.\d{2}'
        prices = re.findall(price_pattern, line)
        
        if prices:
            # Extract item name (everything before the price)
            item_name = line[:line.find(prices[-1])].strip()
            if item_name:
                items.append({
                    'item': item_name,
                    'price': float(prices[-1].replace('$', '')),
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
    
    return pd.DataFrame(items)

def main():
    st.title("Receipt Scanner")
    
    # Add file uploader that accepts images
    image_file = st.camera_input("Take a picture of your receipt")
    
    if image_file is not None:
        # Display the uploaded image
        image = Image.open(image_file)
        st.image(image, caption='Uploaded Receipt', use_column_width=True)
        
        # Add a button to process the image
        if st.button('Process Receipt'):
            with st.spinner('Processing receipt...'):
                try:
                    # Process the image and extract line items
                    df = process_receipt_image(image)
                    
                    # Display the extracted items
                    st.subheader("Extracted Items")
                    st.dataframe(df)
                    
                    # Add download button for CSV
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download data as CSV",
                        data=csv,
                        file_name="receipt_items.csv",
                        mime="text/csv",
                    )
                    
                except Exception as e:
                    st.error(f"Error processing receipt: {str(e)}")
    
    # Add some usage instructions
    st.markdown("""
    ### How to use:
    1. Click the camera button to take a picture of your receipt
    2. Make sure the receipt is well-lit and the text is clearly visible
    3. Click 'Process Receipt' to extract the items
    4. Download the extracted data as CSV if needed
    """)

if __name__ == '__main__':
    main()
