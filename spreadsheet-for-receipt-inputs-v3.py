import streamlit as st
import pandas as pd
from datetime import datetime

def convert_df(df):
    """Convert a DataFrame to a CSV string encoded as UTF-8."""
    if df is None or df.empty:
        st.warning("No data available for download.")
        return None
    return df.to_csv(index=False).encode('utf-8')

def calculate_totals(items, tax_rate):
    """Calculate subtotal, tax amount, and total."""
    subtotal = sum(item['Price'] for item in items if item['Price'] > 0)
    tax_amount = subtotal * (tax_rate / 100)  # Convert tax percentage to decimal
    total = subtotal + tax_amount
    return subtotal, tax_amount, total

def main():
    st.title('Simplified Receipt Input Application')

    # Initialize session state
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            'company_name': '',
            'date': datetime.now().date(),
            'items': [],
            'tax_rate': 0.0,
            'total': 0.0
        }
    if 'item_count' not in st.session_state:
        st.session_state.item_count = 0
    if 'receipt_data' not in st.session_state:
        st.session_state.receipt_data = None
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False

    # Receipt Input Form
    with st.form(key='receipt_form'):
        st.session_state.form_data['company_name'] = st.text_input('Company Name', st.session_state.form_data['company_name'])

        st.subheader('Line Items')
        for i in range(st.session_state.item_count):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                item_name = st.text_input(f'Item Name {i+1}', key=f'item_name_{i}')
            with col2:
                price = st.number_input(f'Price {i+1}', min_value=0.0, format="%.2f", key=f'price_{i}')
            with col3:
                item_date = st.date_input(f'Date {i+1}', datetime.now().date(), key=f'item_date_{i}')
            
            if i < len(st.session_state.form_data['items']):
                st.session_state.form_data['items'][i] = {'Item': item_name, 'Price': price, 'Date': item_date}
            else:
                st.session_state.form_data['items'].append({'Item': item_name, 'Price': price, 'Date': item_date})

        if st.form_submit_button('Add Item', type="secondary"):
            st.session_state.item_count += 1
            st.experimental_rerun()

        # Tax rate input (as percentage)
        tax_rate = st.number_input('Tax Rate (%)', min_value=0.0, format="%.2f", value=st.session_state.form_data['tax_rate'])
        st.session_state.form_data['tax_rate'] = tax_rate

        # Calculate and display running totals
        valid_items = [item for item in st.session_state.form_data['items'] if item['Item'] and item['Price'] > 0]
        subtotal, tax_amount, total = calculate_totals(valid_items, tax_rate)

        # Display running totals
        st.write(f"Subtotal: ${subtotal:.2f}")
        st.write(f"Tax Amount: ${tax_amount:.2f}")
        st.write(f"Total: ${total:.2f}")

        st.session_state.form_data['date'] = st.date_input('Date', st.session_state.form_data['date'])

        # Submit form
        if st.form_submit_button('Save Receipt'):
            if valid_items:
                st.session_state.receipt_data = pd.DataFrame({
                    'Company': [st.session_state.form_data['company_name']] * len(valid_items),
                    'Date': [item['Date'] for item in valid_items],
                    'Item': [item['Item'] for item in valid_items],
                    'Price': [item['Price'] for item in valid_items],
                    'Tax Rate': [tax_rate] * len(valid_items),
                    'Tax Amount': [tax_amount / len(valid_items)] * len(valid_items),  # Distribute tax equally
                    'Total': [total] * len(valid_items)
                })
                st.session_state.form_submitted = True
            else:
                st.warning("Please provide at least one valid item.")
                st.session_state.form_submitted = False

    # Handle download button outside the form
    if st.session_state.form_submitted:
        st.write("Receipt Details:")
        st.dataframe(st.session_state.receipt_data)

        csv_data = convert_df(st.session_state.receipt_data)
        if csv_data:
            st.download_button(
                label="Download Receipt",
                data=csv_data,
                file_name=f"receipt_{st.session_state.form_data['date'].strftime('%Y%m%d')}.csv",
                mime='text/csv',
            )

if __name__ == "__main__":
    main()
