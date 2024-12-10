import streamlit as st
import os
import pandas as pd
import requests
import subprocess
import sys

try:
    import matplotlib.pyplot as plt
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib.pyplot as plt

url = "https://api.groq.com/openai/v1/chat/completions"

variable_name = "GKEY"
api_key = os.getenv(variable_name)

if api_key:
    st.write("API key loaded successfully!")
else:
    st.error("API key not found. Please set the 'GROQ_API_KEY' environment variable.")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def get_response(prompt):
    system_prompt = "Give a summary report on the data and explain what the nature of the activity is. Be verbose and identify fields you recognize. Explain each field that you recognize and what kind of data it contains. Suggest possible investigative directions. Ignore rows with a logstatus of NODATA because those are just errors and not threats. Keep in mind the following knowledge: if there are values like sts.amazonaws.com, they are cloudtrail events. If there are interface-id and action fields, they are vpc flow log events. If there are fields whose names begin with k8s, they are Kubernetes events."

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code != 200:
        st.write("Response Status Code:", response.status_code)
        st.write("Response Content:", response.text)

    if response.status_code == 200:
        return response.json()
    else:
        return None

def format_response(response):
    markdown_response = "### API Response\n\n"
    if 'choices' in response:
        for i, choice in enumerate(response['choices']):
            markdown_response += f"#### Choice {i + 1}\n"
            markdown_response += f"- **Role**: {choice['message']['role']}\n"
            markdown_response += f"- **Content**: {choice['message']['content']}\n\n"
    else:
        markdown_response += "No choices found in the response."
    return markdown_response

def run():
    st.title("Anomaly Detection")

    uploaded_file = st.file_uploader("Upload your CSV log file:", type=["csv"])
    csv_content = None
    df = None
    deduplicated_csv_content = None

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.markdown("### Uploaded Data (Showing First 100 Rows)")
            st.dataframe(df.head(100))
            csv_content = df.head(100).to_string(index=False)
        except Exception as e:
            st.error(f"Error loading CSV file: {e}")

    # Anomaly Detection Section
    if df is not None:
        st.markdown("## Anomaly Detection: Choose combinations of least frequently occurring values for hunting outliers")
        combo_fields = st.multiselect("Select fields for anomaly detection:", options=df.columns.tolist())

        if combo_fields:
            combo_freq = df.groupby(combo_fields).size().reset_index(name='count')
            least_frequent_combos = combo_freq.sort_values(by='count', ascending=True).head(10)
            st.markdown("### 10 Least Frequent Combinations of Selected Fields:")
            st.dataframe(least_frequent_combos)
            anomaly_content = least_frequent_combos.to_string(index=False)
        else:
            anomaly_content = None
    else:
        anomaly_content = None

    # Prompt input and response section
    include_csv = st.checkbox("Include table contents in the prompt")
    st.markdown("### Enter Your Prompt:")
    prompt = st.text_input("Enter your prompt for Groq:")

    if st.button("Submit"):
        if prompt.strip() or (include_csv and deduplicated_csv_content):  
            if include_csv and deduplicated_csv_content:
                prompt = f"{prompt}\n\n### Table Data (First 100 Rows after Deduplication):\n{deduplicated_csv_content}"
            if anomaly_content:
                prompt += f"\n\n### Anomaly Detection Results:\n{anomaly_content}"

            #st.markdown("### Full Prompt Sent to API")
            #st.text(prompt)

            with st.spinner("Fetching answer from Groq..."):
                response = get_response(prompt)
            
            if response:
                markdown_response = format_response(response)
                st.markdown(markdown_response, unsafe_allow_html=True)
            else:
                st.error("Failed to get response from the API. Please check your API key, endpoint, and input format.")
        else:
            st.warning("Please enter a valid prompt and optionally include CSV data.")
