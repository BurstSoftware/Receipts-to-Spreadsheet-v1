import streamlit as st
import pandas as pd
from datetime import datetime

def convert_df(df):
    """Convert a DataFrame to a CSV string encoded as UTF-8."""
    if df is None or df.empty:
        st.warning("No data available for download.")
        return None
    return df.to_csv(index=False).encode('utf-8')

def calculate_totals(items, tax_amount):
    """Calculate subtotal, total tax, and total based on items and a single tax amount."""
    subtotal = sum(item['Quantity'] * item['Price'] for item in items if item['Price'] > 0 and item['Quantity'] > 0)
    total = subtotal + tax_amount
    return subtotal, tax_amount, total

def main():
    st.title('Simplified Receipt Input Application')

    # Initialize session state
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            'company_name': '',
            'items': [],
            'tax_amount': 0.0,
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
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])  # Four columns for Item Name, Quantity, Price, Date
            with col1:
                item_name = st.text_input(f'Item Name {i+1}', key=f'item_name_{i}')
            with col2:
                quantity = st.number_input(f'Quantity {i+1}', min_value=0, value=1, step=1, key=f'quantity_{i}')
            with col3:
                price = st.number_input(f'Price {i+1}', min_value=0.0, format="%.2f", key=f'price_{i}')
            with col4:
                item_date = st.date_input(f'Date {i+1}', datetime.now().date(), key=f'item_date_{i}')
            
            if i < len(st.session_state.form_data['items']):
                st.session_state.form_data['items'][i] = {
                    'Item': item_name,
                    'Quantity': quantity,
                    'Price': price,
                    'Date': item_date
                }
            else:
                st.session_state.form_data['items'].append({
                    'Item': item_name,
                    'Quantity': quantity,
                    'Price': price,
                    'Date': item_date
                })

        if st.form_submit_button('Add Item', type="secondary"):
            st.session_state.item_count += 1
            st.experimental_rerun()

        # Single Tax Amount input below line items
        tax_amount = st.number_input('Tax Amount ($)', min_value=0.0, format="%.2f", value=st.session_state.form_data['tax_amount'])
        st.session_state.form_data['tax_amount'] = tax_amount

        # Calculate and display running totals
        valid_items = [item for item in st.session_state.form_data['items'] if item['Item'] and item['Price'] > 0 and item['Quantity'] > 0]
        subtotal, total_tax, total = calculate_totals(valid_items, tax_amount)

        # Display running totals
        st.write(f"Subtotal: ${subtotal:.2f}")
        st.write(f"Tax Amount: ${total_tax:.2f}")
        st.write(f"Total: ${total:.2f}")

        # Submit form
        if st.form_submit_button('Save Receipt'):
            if valid_items:
                # Create separate DataFrames for line items, subtotal, tax, and total
                # Line items DataFrame
                line_items_df = pd.DataFrame({
                    'Company': [st.session_state.form_data['company_name']] * len(valid_items),
                    'Date': [item['Date'] for item in valid_items],
                    'Item': [item['Item'] for item in valid_items],
                    'Quantity': [item['Quantity'] for item in valid_items],
                    'Price': [item['Price'] for item in valid_items],
                    'Amount': [item['Quantity'] * item['Price'] for item in valid_items]
                })

                # Subtotal row
                subtotal_row = pd.DataFrame({
                    'Company': [st.session_state.form_data['company_name']],
                    'Date': [valid_items[0]['Date']],
                    'Item': ['SUBTOTAL'],
                    'Quantity': [''],
                    'Price': [''],
                    'Amount': [subtotal]
                })

                # Total Tax row
                tax_row = pd.DataFrame({
                    'Company': [st.session_state.form_data['company_name']],
                    'Date': [valid_items[0]['Date']],
                    'Item': ['TAX'],
                    'Quantity': [''],
                    'Price': [''],
                    'Amount': [tax_amount]
                })

                # Total row
                total_row = pd.DataFrame({
                    'Company': [st.session_state.form_data['company_name']],
                    'Date': [valid_items[0]['Date']],
                    'Item': ['TOTAL'],
                    'Quantity': [''],
                    'Price': [''],
                    'Amount': [total]
                })

                # Concatenate all rows into a single DataFrame
                st.session_state.receipt_data = pd.concat([line_items_df, subtotal_row, tax_row, total_row], ignore_index=True)
                st.session_state.form_submitted = True
            else:
                st.warning("Please provide at least one valid item.")
                st.session_state.form_submitted = False

    # Handle download button outside the form
    if st.session_state.form_submitted and valid_items:
        st.write("Receipt Details:")
        st.dataframe(st.session_state.receipt_data)

        csv_data = convert_df(st.session_state.receipt_data)
        if csv_data:
            st.download_button(
                label="Download Receipt",
                data=csv_data,
                file_name=f"receipt_{valid_items[0]['Date'].strftime('%Y%m%d')}.csv",
                mime='text/csv',
            )

if __name__ == "__main__":
    main()
