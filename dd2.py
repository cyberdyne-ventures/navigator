import streamlit as st
import pandas as pd
from charset_normalizer import from_bytes
import io  

# Detect Encoding Function
def detect_encoding(uploaded_file):
    """
    Detect the encoding of the uploaded file.
    """
    raw_data = uploaded_file.read()  # Read the file content as bytes
    uploaded_file.seek(0)  # Reset the pointer after reading
    detected = from_bytes(raw_data).best()
    return detected.encoding if detected else "utf-8"

# Function to style and wrap DataFrame
def style_dataframe_for_wrapping(df):
    """
    Convert a DataFrame to an HTML table with styled text wrapping.
    """
    return df.to_html(escape=False, index=False).replace(
        "<table>",
        """<table style="word-wrap: break-word; table-layout: fixed; width: 100%; border-collapse: collapse;">
           <style>
               td, th {
                   word-wrap: break-word;
                   max-width: 200px;  /* Adjust as needed */
                   white-space: normal;
                   overflow-wrap: break-word;
                   padding: 8px;
               }
           </style>
        """
    )

# Main Streamlit Application
def run():
    st.title("Deduplication FTW")
    
    # File Upload Section
    uploaded_file = st.file_uploader("Upload your Python or CSV file:", type=["py", "csv"])
    df = None  # Initialize df to avoid potential UnboundLocalError
    if uploaded_file is None:
        st.info("Please upload a CSV file to get started.")
        return
    
    if uploaded_file is not None:
        try:
            # Detect encoding
            encoding = detect_encoding(uploaded_file)
            st.success(f"Detected encoding: {encoding}")
            
            # Load and display the file if it's a CSV
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file, encoding=encoding)

                st.write("Preview of the uploaded CSV:")

                # Toggle box to show entire DataFrame or head
                show_all = st.checkbox("Show entire DataFrame", value=False)
                
                if show_all:
                    st.write("Displaying entire DataFrame:")
                    st.dataframe(df)
                else:
                    st.write("Displaying top rows of DataFrame:")
                    st.dataframe(df.head())

            else:
                st.write("Uploaded file is not a CSV. Only encoding was detected.")
        
        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")

    # Deduplication Section
    if df is not None:
        st.markdown("## Deduplication Options")
        dedupe_fields = st.multiselect("Choose fields to deduplicate:", options=df.columns.tolist())
        
        if dedupe_fields:
            deduplicated_df = df.drop_duplicates(subset=dedupe_fields)
            st.markdown("### Data after Deduplication")
            
            # Predefined list of fields to display
            predefined_fields = ["stageTimestamp", "stage", "requestURI",  "verb", 
                                 "user", "sourceIPs", "userAgent", "objectRef",
                                 "responseStatus", "annotations"]  # Replace with your desired field names
            
            # Validate predefined fields exist in the DataFrame
            valid_fields = [field for field in predefined_fields if field in deduplicated_df.columns]
            
            # Add checkbox to toggle between predefined fields and all fields
            show_all_fields = st.checkbox("Show all fields", value=False)
            
            if show_all_fields:
                # Use all fields in the DataFrame
                filtered_df = deduplicated_df.head
            else:
                if valid_fields:
                    # Filter DataFrame to include only the valid predefined fields
                    filtered_df = deduplicated_df[valid_fields].head
                else:
                    st.warning("None of the predefined fields exist in the dataset. Please check your field names.")
                    filtered_df = pd.DataFrame()  # Empty DataFrame for fallback

# Add Export Button
            if not filtered_df.empty:
    # Convert DataFrame to CSV in binary format
                csv_buffer = io.BytesIO()
                filtered_df.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)
    
                st.download_button(
                    label="Export Deduplicated Data to CSV",
                    data=csv_buffer.getvalue(),  # Get the binary content
                    file_name="deduplicated_data.csv",
                    mime="text/csv"
    )
            # Convert to styled HTML table
            if not filtered_df.empty:
                styled_table = style_dataframe_for_wrapping(filtered_df)
                st.markdown(styled_table, unsafe_allow_html=True)

            else:
                st.warning("None of the predefined fields exist in the dataset. Please check your field names.")
        else:
            st.info("Select fields for deduplication to see the result.")
    else:
        st.info("Please upload a CSV file to enable deduplication options.")


if __name__ == "__main__":
    run()
