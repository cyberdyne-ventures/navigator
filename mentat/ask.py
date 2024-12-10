import streamlit as st
import pandas as pd
import requests
import os

# Define the API endpoint and your API key
url = "https://api.groq.com/openai/v1/chat/completions"
api_key = "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"

# Define the headers
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def get_response(prompt):
    # Define the system prompt
    system_prompt = "Give a summary report on the data and explain what the nature of the activity is. Be verbose and identify fields you recognize. Explain each field that you recognize and what kind of data it contains. Suggest possible investigative directions. Ignore rows with a logstatus of NODATA becuase those are just errors and not threats. Keep in mind the following knowledge: if there are values like sts.amazonaws.com, they are cloudtrail events. If there are interface-id and action fields, they are vpc flow log events. If there are fields whose names begin with k8s, they are Kubernetes events."

    # Combine the system prompt with the user prompt
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": system_prompt},  # System prompt
            {"role": "user", "content": prompt}           # User-entered prompt
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    # Log the response status and body for debugging
    if response.status_code != 200:
    # Log the response status and body for debugging
        st.write("Response Status Code:", response.status_code)
        st.write("Response Content:", response.text)

    if response.status_code == 200:
        return response.json()
    else:
        return None

def format_response(response):
    markdown_response = "# API Response\n\n"
    if 'choices' in response:
        for i, choice in enumerate(response['choices']):
            markdown_response += f"#### Choice {i + 1}\n"
            markdown_response += f"- **Role**: {choice['message']['role']}\n"
            markdown_response += f"- **Content**: {choice['message']['content']}\n\n"
    else:
        markdown_response += "No choices found in the response."
    return markdown_response

def run():  # Define the run function for the page
    st.title("AI Assisted Data Investigation")

    # File uploader for CSV
    uploaded_file = st.file_uploader("Upload your CSV file:", type=["csv"])
    csv_content = None
    if uploaded_file is not None:
        try:
            # Load CSV into a pandas DataFrame
            df = pd.read_csv(uploaded_file)
            st.markdown("### Uploaded Data (Showing First 50 Rows)")
            st.dataframe(df.head(100))  # Display the first 200 rows of the CSV
            
            # Convert the first 200 rows to a string for appending to the prompt
            csv_content = df.head(100).to_string(index=False)
        except Exception as e:
            st.error(f"Error loading CSV file: {e}")

    # Checkbox to include CSV content in the prompt
    include_csv = st.checkbox("Include table contents in the prompt")

    # Prompt input and response section
    st.markdown("### Enter Your Prompt Below")
    prompt = st.text_input("Enter your prompt for Groq:")

    if st.button("Submit"):
        if prompt.strip():  # Validate input
            # Append CSV content to the prompt if checkbox is checked
            if include_csv and csv_content:
                prompt = f"{prompt}\n\n### Table Data (First 100 Rows):\n{csv_content}"
            
            # Display the entire prompt being sent
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
            st.warning("Please enter a valid prompt.")


