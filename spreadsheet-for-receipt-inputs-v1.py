import streamlit as st
import pandas as pd
from datetime import datetime
from base64 import b64encode

def convert_df(df):
    return df.to_csv(index=False)

def get_table_download_link(df):
    """Generate a link allowing the data in a given panda dataframe to be downloaded"""
    csv = df.to_csv(index=False)
    b64 = b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="receipt_{datetime.now().strftime("%Y%m%d")}.csv">Download CSV File</a>'
    return href

def main():
    st.title('Simplified Receipt Input Application')

    # ... (previous session state and form setup code here) ...

    if submit:
        items = [item for item in st.session_state.form_data['items'] if item['Item'] and item['Price'] > 0]
        
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
                st.markdown(get_table_download_link(receipt_data), unsafe_allow_html=True)
            else:
                st.warning('No items to download.')
        else:
            st.warning('Please enter at least one valid item.')

if __name__ == "__main__":
    main()
