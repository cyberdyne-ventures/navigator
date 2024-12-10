import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set page layout to wide mode
st.set_page_config(layout="wide")

# Inject CSS to make the table wider
def inject_css():
    st.markdown(
        """
        <style>
        .dataframe-container {
            width: 100% !important;
        }
        </style>
        """, unsafe_allow_html=True
    )

inject_css()

# File uploader for CSV file
uploaded_file = st.file_uploader("Upload your CSV log file, sanitizing first if necessary. Do not upload data that is not yours!", type=["csv"])

if uploaded_file is not None:
    try:
        # Load CSV data into a pandas DataFrame
        df = pd.read_csv(uploaded_file)
        
        # Display the raw data with a variable number of rows
        st.markdown("## The Datanator: Here is the uploaded data using the first row as column names")  # Add prominent title
        num_lines = st.slider('Select number of lines to view', min_value=5, max_value=len(df), value=10)
        
        # Display table with CSS for full width
        st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
        st.dataframe(df.head(num_lines))
        st.markdown('</div>', unsafe_allow_html=True)

        # Deduplication Section
        st.markdown("## The Deduplinator: Most logs deduplicate by large ratios, making review possible for hunters")
        
        dedupe_fields = st.multiselect("Choose fields to deduplicate:", options=df.columns.tolist())
        
        if dedupe_fields:
            deduplicated_df = df.drop_duplicates(subset=dedupe_fields)
            
            num_lines_after_dedupe = st.slider(
                'Select number of deduplicated rows to view',
                min_value=5,
                max_value=len(deduplicated_df),
                value=min(10, len(deduplicated_df))
            )
            
            st.markdown(f"### Data after deduplication (First {num_lines_after_dedupe} rows):")
            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
            st.dataframe(deduplicated_df.head(num_lines_after_dedupe))
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Option to download deduplicated data
            csv = deduplicated_df.to_csv(index=False)
            st.download_button(label="Download Deduplicated CSV", data=csv, file_name="deduplicated_logs.csv", mime="text/csv")
        else:
            st.markdown("Please select fields to deduplicate the data.")
        
        # Anomaly Detection Section
        st.markdown("## Anomaly Detection: Choose combinations of least frequently occurring values for hunting outliers")
        
        combo_fields = st.multiselect("I'd consider combinations like source IP, user context, actions and methods, etc., but when in doubt, experiment.", options=df.columns.tolist())

        if combo_fields:
            combo_freq = df.groupby(combo_fields).size().reset_index(name='count')
            least_frequent_combos = combo_freq.sort_values(by='count', ascending=True).head(10)
            
            st.markdown("### 10 Least Frequent Combinations of Selected Fields:")
            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
            st.dataframe(least_frequent_combos)
            st.markdown('</div>', unsafe_allow_html=True)

            # Visualization of least frequent combinations
            st.markdown("### Visualization of Least Frequent Combinations:")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.barh(least_frequent_combos[combo_fields].apply(lambda row: ' | '.join(row.astype(str)), axis=1), least_frequent_combos['count'])
            ax.set_xlabel('Count')
            ax.set_ylabel('Combination')
            ax.set_title('Least Frequent Combinations')
            st.pyplot(fig)
    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload a CSV file to get started.")
