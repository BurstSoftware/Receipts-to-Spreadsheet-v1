import streamlit as st
import pandas as pd
from datetime import datetime

def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

def main():
    st.title('Simplified Receipt Input Application')

    # Initialize session state
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            'company_name': '',
            'date': datetime.now().date(),
            'items': [],
            'tax': 0.0,
            'total': 0.0
        }

    # Receipt Input Form
    with st.form(key='receipt_form'):
        st.session_state.form_data['company_name'] = st.text_input('Company Name', st.session_state.form_data['company_name'])
        st.session_state.form_data['date'] = st.date_input('Date', st.session_state.form_data['date'])
        st.session_state.form_data['tax'] = st.number_input('Tax', min_value=0.0, format="%.2f", value=st.session_state.form_data['tax'])
        st.session_state.form_data['total'] = st.number_input('Total', min_value=0.0, format="%.2f", value=st.session_state.form_data['total'])
        
        # Dynamic line item inputs
        st.subheader('Line Items')
        if 'item_count' not in st.session_state:
            st.session_state.item_count = 0

        # Add new item input
        for i in range(st.session_state.item_count):
            col1, col2 = st.columns(2)
            with col1:
                item_name = st.text_input(f'Item Name {i+1}', key=f'item_name_{i}')
            with col2:
                price = st.number_input(f'Price {i+1}', min_value=0.0, format="%.2f", key=f'price_{i}')
            st.session_state.form_data['items'].append({'Item': item_name, 'Price': price})
        
        # Button to add more items
        if st.button('Add Item'):
            st.session_state.item_count += 1

        submit = st.form_submit_button('Save Receipt')

        if submit:
            # Validate and prepare items data
            items = []
            for item in st.session_state.form_data['items']:
                if item['Item'] and item['Price'] > 0:
                    items.append(item)
                elif item['Item'] or item['Price'] > 0:
                    st.error(f"Both item name and price must be provided for item: {item['Item'] or 'Unknown'}")
            
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
                st.warning('Please enter at least one valid item.')

if __name__ == "__main__":
    main()
