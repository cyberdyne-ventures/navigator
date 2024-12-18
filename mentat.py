import streamlit as st
import importlib

#st.set_page_config(layout="wide")
st.set_page_config(
    layout="wide",  
    #theme="dark",
    page_title="AI Assisted Threat Hunting",  
    page_icon="🧐"  
)
st.sidebar.image("logo.png", use_column_width=True) 

st.sidebar.title("Navigation")
pages = {
    "Home": "home",
    "AI Interface": "ask",    
    "Anomaly Detection": "anomalies2",
    "Data Compression": "dd2"
}

selection = st.sidebar.radio("Go to", list(pages.keys()))

module_name = pages[selection]
module = importlib.import_module(module_name)
module.run()



