import streamlit as st

# Access a single key
api_key = st.secrets["GKEY"]

# Displaying values (for demonstration; avoid displaying sensitive info in production)
st.write(f"API Key: {api_key}")
