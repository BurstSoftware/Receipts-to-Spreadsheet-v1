import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Function to convert DataFrame to CSV bytes
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Function to parse line items with error handling
def parse_line_items(line_items):
    items = []
    for line in line_items.split('\n'):
        line = line.strip()
        if line:
            parts = line.split(',', 1)
            if len(parts) == 2:
                item_name, price_str = parts
                try:
                    price = float(price_str.strip())
                    items.append({'Item': item_name.strip(), 'Price': price})
                except ValueError:
                    st.error(f"Invalid price format for item: {item_name}")
            else:
                st.error(f"Item format incorrect for: {line}")
    return items

# Main application
def main():
    st.title('Receipt Input Application')

    # State to hold form data
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            'company_name': '',
            'date': datetime.now().date(),
            'time': datetime.now().time(),
            'line_items': '',
            'tax': 0.0,
            'sub_total': 0.0,
            'total': 0.0
        }

    # Form for input
    with st.form(key='receipt_form'):
        st.session_state.form_data['company_name'] = st.text_input('Company Name', st.session_state.form_data['company_name'])
        st.session_state.form_data['date'] = st.date_input('Date', st.session_state.form_data['date'])
        st.session_state.form_data['time'] = st.time_input('Time', st.session_state.form_data['time'])
        st.session_state.form_data['line_items'] = st.text_area('Line Items (one per line, format: Item Name, Price)', st.session_state.form_data['line_items'])
        st.session_state.form_data['tax'] = st.number_input('Tax', min_value=0.0, format="%.2f", value=st.session_state.form_data['tax'])
        st.session_state.form_data['sub_total'] = st.number_input('Sub Total', min_value=0.0, format="%.2f", value=st.session_state.form_data['sub_total'])
        st.session_state.form_data['total'] = st.number_input('Total', min_value=0.0, format="%.2f", value=st.session_state.form_data['total'])
        
        submit_button = st.form_submit_button(label='Save Receipt')

        if submit_button:
            items = parse_line_items(st.session_state.form_data['line_items'])
            if items:
                receipt_data = {
                    'Company': [st.session_state.form_data['company_name']] * len(items),
                    'Date': [st.session_state.form_data['date']] * len(items),
                    'Time': [st.session_state.form_data['time']] * len(items),
                    'Item': [item['Item'] for item in items],
                    'Price': [item['Price'] for item in items],
                    'Tax': [st.session_state.form_data['tax']] * len(items),
                    'Sub Total': [st.session_state.form_data['sub_total']] * len(items),
                    'Total': [st.session_state.form_data['total']] * len(items)
                }
                
                df = pd.DataFrame(receipt_data)
                
                # Download CSV
                csv = convert_df(df)
                st.download_button(
                    label="Download Receipt as CSV",
                    data=csv,
                    file_name=f"receipt_{st.session_state.form_data['date'].strftime('%Y%m%d')}.csv",
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
