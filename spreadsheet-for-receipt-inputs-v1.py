import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Function to convert DataFrame to CSV
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Main application
def main():
    st.title('Receipt Input Application')

    # Form for input
    with st.form(key='receipt_form'):
        company_name = st.text_input('Company Name')
        date = st.date_input('Date')
        time = st.time_input('Time')
        line_items = st.text_area('Line Items (one per line, format: Item Name, Price)')
        tax = st.number_input('Tax', min_value=0.0, format="%.2f")
        sub_total = st.number_input('Sub Total', min_value=0.0, format="%.2f")
        total = st.number_input('Total', min_value=0.0, format="%.2f")
        
        submit_button = st.form_submit_button(label='Save Receipt')

        if submit_button:
            # Parse line items with error handling
            items = []
            for line in line_items.split('\n'):
                if line.strip():  # Skip empty lines
                    parts = line.split(',', 1)
                    if len(parts) == 2:
                        try:
                            items.append((parts[0].strip(), float(parts[1].strip())))
                        except ValueError:
                            st.error(f"Invalid price format for item: {parts[0]}")
                    else:
                        st.error(f"Item format incorrect for: {line}")
            
            if items:
                receipt_data = {
                    'Company': [company_name] * len(items),
                    'Date': [date] * len(items),
                    'Time': [time] * len(items),
                    'Item': [item[0] for item in items],
                    'Price': [item[1] for item in items],
                    'Tax': [tax] * len(items),
                    'Sub Total': [sub_total] * len(items),
                    'Total': [total] * len(items)
                }
                
                df = pd.DataFrame(receipt_data)
                
                # Download CSV
                csv = convert_df(df)
                st.download_button(
                    label="Download Receipt as CSV",
                    data=csv,
                    file_name=f"receipt_{date.strftime('%Y%m%d')}.csv",
                    mime='text/csv',
                )
            else:
                st.warning('No valid items were entered. Please check the format of your line items.')

    # Upload and append to existing CSV
    st.subheader('Upload Existing Receipt CSV')
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        existing_df = pd.read_csv(uploaded_file)
        st.write("Current Data:")
        st.write(existing_df)

        # Add new data to existing data
        if 'df' in locals():  # If new data was added
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            csv = convert_df(combined_df)
            st.download_button(
                label="Download Updated Receipt as CSV",
                data=csv,
                file_name=f"receipt_updated_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv',
            )

if __name__ == "__main__":
    main()
