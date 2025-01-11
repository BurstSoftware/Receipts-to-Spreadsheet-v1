import streamlit as st
import pandas as pd
from datetime import datetime

def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

def parse_line_items(line_items):
    items = []
    for line in line_items.split('\n'):
        if line.strip():
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

def main():
    st.title('Simplified Receipt Input Application')

    # Initialize session state
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            'company_name': '',
            'date': datetime.now().date(),
            'line_items': '',
            'tax': 0.0,
            'total': 0.0
        }

    # Receipt Input Form
    with st.form(key='receipt_form'):
        st.session_state.form_data['company_name'] = st.text_input('Company Name', st.session_state.form_data['company_name'])
        st.session_state.form_data['date'] = st.date_input('Date', st.session_state.form_data['date'])
        st.session_state.form_data['line_items'] = st.text_area('Line Items (Item Name, Price per line)', st.session_state.form_data['line_items'])
        st.session_state.form_data['tax'] = st.number_input('Tax', min_value=0.0, format="%.2f", value=st.session_state.form_data['tax'])
        st.session_state.form_data['total'] = st.number_input('Total', min_value=0.0, format="%.2f", value=st.session_state.form_data['total'])
        
        submit = st.form_submit_button('Save Receipt')

        if submit:
            items = parse_line_items(st.session_state.form_data['line_items'])
            if items:
                receipt_data = pd.DataFrame({
                    'Company': [st.session_state.form_data['company_name']] * len(items),
                    'Date': [st.session_state.form_data['date']] * len(items),
                    'Item': [item['Item'] for item in items],
                    'Price': [item['Price'] for item in items],
                    'Tax': [st.session_state.form_data['tax']] * len(items),
                    'Total': [st.session_state.form_data['total']] * len(items)
                })
                
                st.write("Receipt Details:", receipt_data)
                
                if not receipt_data.empty:
                    csv = convert_df(receipt_data)
                    st.download_button(
                        label="Download Receipt",
                        data=csv,
                        file_name=f"receipt_{st.session_state.form_data['date'].strftime('%Y%m%d')}.csv",
                        mime='text/csv',
                    )
                else:
                    st.warning('No items to download.')
            else:
                st.warning('Please enter valid line items.')

if __name__ == "__main__":
    main()
