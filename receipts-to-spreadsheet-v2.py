import streamlit as st
from PIL import Image
import io
import re
import pandas as pd
from datetime import datetime
import sys
import subprocess

def check_tesseract():
    try:
        import pytesseract
        return pytesseract
    except ImportError as e:
        st.error("PyTesseract import failed. Please check installation.")
        st.error(f"Error details: {str(e)}")
        return None

def process_receipt_image(image):
    """
    Process the receipt image using OCR and extract relevant information,
    assuming left column contains text and right column contains numbers
    """
    pytesseract = check_tesseract()
    if not pytesseract:
        return pd.DataFrame()

    try:
        # Convert the image to text using pytesseract
        text = pytesseract.image_to_string(image)
        st.write("Extracted text:", text)  # Debug output
        
        # Parse the text to extract line items
        lines = text.split('\n')
        items = []
        
        # Enhanced parsing logic for left-text, right-number format
        for line in lines:
            # Skip empty lines and header/footer text
            if not line.strip() or any(skip in line.lower() for skip in ['total', 'subtotal', 'tax', 'change', 'cash', 'credit', 'phone', 'receipt']):
                continue
            
            # Look for price patterns at the end of the line
            price_pattern = r'\$?\d+\.\d{2}'
            prices = re.findall(price_pattern, line)
            
            if prices:
                # Get the last price in the line (rightmost)
                price = prices[-1]
                
                # Extract item name (everything before the last price)
                item_name = line[:line.rfind(price)].strip()
                
                # Remove any extra prices from the item name
                for p in prices[:-1]:
                    item_name = item_name.replace(p, '').strip()
                
                # Remove common separators and clean up the item name
                item_name = re.sub(r'[.]{2,}|[@\t]+', ' ', item_name).strip()
                
                # Only add if we have both an item name and price
                if item_name and not item_name.isspace():
                    items.append({
                        'item': item_name,
                        'price': float(price.replace('$', '')),
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
        
        # Create DataFrame and sort by price
        df = pd.DataFrame(items)
        if not df.empty:
            df = df.sort_values('price', ascending=False)
        
        return df
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return pd.DataFrame()

def main():
    st.title("Receipt Scanner")
    
    # Display system information
    st.sidebar.write("System Information:")
    st.sidebar.write(f"Python version: {sys.version}")
    
    try:
        # Check Tesseract version
        tesseract_version = subprocess.check_output(['tesseract', '--version']).decode()
        st.sidebar.write(f"Tesseract version: {tesseract_version.split()[1]}")
    except Exception as e:
        st.sidebar.error(f"Tesseract not found: {str(e)}")
    
    # Add file uploader that accepts images
    image_file = st.camera_input("Take a picture of your receipt")
    
    if image_file is not None:
        try:
            # Display the uploaded image
            image = Image.open(image_file)
            st.image(image, caption='Uploaded Receipt', use_column_width=True)
            
            # Add a button to process the image
            if st.button('Process Receipt'):
                with st.spinner('Processing receipt...'):
                    # Process the image and extract line items
                    df = process_receipt_image(image)
                    
                    if not df.empty:
                        # Display the extracted items
                        st.subheader("Extracted Items")
                        st.dataframe(df)
                        
                        # Add summary statistics
                        st.subheader("Summary")
                        st.write(f"Total Items: {len(df)}")
                        st.write(f"Total Amount: ${df['price'].sum():.2f}")
                        
                        # Add download button for CSV
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download data as CSV",
                            data=csv,
                            file_name="receipt_items.csv",
                            mime="text/csv",
                        )
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    # Add some usage instructions
    st.markdown("""
    ### How to use:
    1. Click the camera button to take a picture of your receipt
    2. Make sure the receipt is well-lit and the text is clearly visible
    3. Click 'Process Receipt' to extract the items
    4. Download the extracted data as CSV if needed
    
    ### Tips for best results:
    - Ensure good lighting when taking the picture
    - Keep the receipt flat and avoid wrinkles
    - Make sure all text is clearly visible
    - Align the receipt vertically in the frame
    """)

if __name__ == '__main__':
    main()
