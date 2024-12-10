import streamlit as st
import importlib

# Set page configuration here
#st.set_page_config(layout="wide")

st.set_page_config(
    layout="wide",  # Enables wide mode,
    #theme="dark",
    page_title="AI Assisted Threat Hunting",  # Sets the page title
    page_icon="🧐"  # Sets the favicon for the tab
)

# Sidebar navigation
st.sidebar.title("Navigation")
pages = {
    "Home": "home",
    "AI Interface": "ask",    
    "Anomaly Detection": "anomalies",
    "Data Compression": "dd"
}

selection = st.sidebar.radio("Go to", list(pages.keys()))

# Load the selected page module dynamically
module_name = pages[selection]
module = importlib.import_module(module_name)
module.run()



