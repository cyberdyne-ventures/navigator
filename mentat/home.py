import sys
import streamlit as st

def run():
    st.image("thufir.gif")  # Replace with your own banner image
    st.title("Mentat: A FOSS Project for AI-Assisted Threat Hunting ")
    st.markdown(
        """
        ### This is the main page. There are several options:
        - AI Interface: Load a dataframe and ask questions about your machine learning detections or conventional detection artifacts.
        - Anomaly Detection: A simple interface for hunting outlier events in a dataframe.
        - Data Compression: A point and click interface for deduplicating rows in a dataframe.
        """
    )

    st.write("Python version:", sys.version)
    st.write("Python executable:", sys.executable)
    
