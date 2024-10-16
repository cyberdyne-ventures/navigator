import streamlit as st
import pandas as pd

# Set page layout to wide mode
st.set_page_config(layout="wide")

# Inject CSS to make the table wider
st.markdown(
    """
    <style>
    .dataframe-container {
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True
)

# File uploader for CSV file
uploaded_file = st.file_uploader("Upload your CSV log file, sanatizing first if necessary. Do not upload data that is not yours!", type=["csv"])

if uploaded_file is not None:
    # Load CSV data into a pandas DataFrame
    df = pd.read_csv(uploaded_file)
    
    # Display the raw data with a variable number of rows
    st.markdown("## The Datanator: Here is the uploaded data using the first row as column names")  # Add prominent title
    num_lines = st.slider('Select number of lines to view', min_value=5, max_value=len(df), value=10)
    
    # Display table with CSS for full width
    st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
    st.dataframe(df.head(num_lines))
    st.markdown('</div>', unsafe_allow_html=True)

    # Add prominent title for the deduplication section
    st.markdown("## The Deduplinator: Most logs deduplicate by large ratios, making review possible for hunters")  # More prominent title for deduplication section
    
    # User selects fields for deduplication
    dedupe_fields = st.multiselect("Choose fields to deduplicate:", options=df.columns.tolist())
    
    if dedupe_fields:
        # Deduplicate the dataframe based on selected fields
        deduplicated_df = df.drop_duplicates(subset=dedupe_fields)
        
        # Let user choose how many rows to return after deduplication
        num_lines_after_dedupe = st.slider(
            'Select number of deduplicated rows to view',
            min_value=5,
            max_value=len(deduplicated_df),
            value=min(10, len(deduplicated_df))  # Ensure default value is within range
        )
        
        st.markdown(f"### Data after deduplication (First {num_lines_after_dedupe} rows):")  # Smaller heading for the output table
        st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
        st.dataframe(deduplicated_df.head(num_lines_after_dedupe))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Option to download deduplicated data
        csv = deduplicated_df.to_csv(index=False)
        st.download_button(label="Download Deduplicated CSV", data=csv, file_name="deduplicated_logs.csv", mime="text/csv")
    else:
        st.markdown("Please select fields to deduplicate the data.")
    
    # Add prominent title for the least frequent combinations section
    st.markdown("## Anomaly Detection: Choose combinations of least frequently occuring values for hunting outliers")  # More prominent title for least frequent combinations section
    
    # New Feature: Display 10 least frequently occurring combinations of selected fields
    combo_fields = st.multiselect("Choose fields for combination analysis:", options=df.columns.tolist())

    if combo_fields:
        # Group by the selected fields and count occurrences
        combo_freq = df.groupby(combo_fields).size().reset_index(name='count')
        
        # Sort by the count to get the least frequent combinations in ascending order
        least_frequent_combos = combo_freq.sort_values(by='count', ascending=True).head(10)
        
        st.markdown("### 10 Least Frequent Combinations of Selected Fields:")  # Smaller heading for output
        st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
        st.dataframe(least_frequent_combos)
        st.markdown('</div>', unsafe_allow_html=True)

