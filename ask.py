import streamlit as st
import pandas as pd
import requests
import os


url = "https://api.groq.com/openai/v1/chat/completions"

#variable_name = "GKEY"
api_key = st.secrets["GKEY"]

if api_key:
    st.write("API key loaded successfully!")
else:
    st.error("API key not found. Please set the 'GROQ_API_KEY' environment variable.")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
prompt = """You are a security threat hunter and detection engineer examining some data that the user has provided.
First, if the table data contains these fields, they are Cloudtrail events:
eventTime: the timestamp
eventSource: the AWS service which was used    
eventName: the name of the API call that was used
awsRegion: the name of the AWS region
sourceIPAddress: the source IP address of the caller
userAgent: the calling user agent    
readOnly: TRUE means the API call was only reading data or objects. FALSE means the API call made changes.
sessionCredentialFromConsole: TRUE means the API call took place interactively in the AWS console in a browser. FALSE means it was programmatic.
userIdentity.type: AssumeRole is a temporary role using an STS token. Root is the superuser for the account. AWSService means it came from an internal AWS service.
userIdentity.principalId: when this contains the word ‘instance” this identifies the EC2 instance that the API call came from.
userIdentity.arn: the user context which made the call.
userIdentity.sessionContext.attributes.mfaAuthenticated: FALSE means the user used multi factor authentication.
errorCode: if this field is not null, it contains the type of error which was returned. If it is null, there was no error.    
errorMessage:  if this field is not null, it contains the details of the error which was returned. If it is null, there was no error.    
response: details of the response to the API call.
request: details of the parameters in the API call that was made.

	If the table data contains these fields, they are VPC flow logs:

account-id: the AWS account number where the flow took place.
interface-id: the ENI (elastic network interface) that sent or received the flow.
srcaddr: the source IP address.
dstaddr: the destination IP address.
srcport: the source port.
dstport: the destination port.
protocol: the protocol number.
packets: the number of packets in the flow.    
bytes: the number of bytes in the flow.
start: the start time of the flow.
end: the end time of the flow.
action: the action taken by a security group. ACCEPT means the flow was permitted. REJECT means the flow was blocked by a security group.

	if the table data contains these fields, they are Kubernetes logs:
Kind: Specifies the type of the log entry (Event in this case).
apiVersion: Indicates the Kubernetes API version of the audit log.
Level: Indicates the verbosity or metadata level of the log entry.
auditID: Unique identifier for the audit event.
Stage: Represents the stage of the request lifecycle - a value of Panic would be a critical error.
requestURI: The URI for the Kubernetes API request.
verb: Specifies the action performed. watch, get and list verbs can be related to discovery and enumeration activity. delete and deletecollection can be relevant to defense evasion. create, update, connect, and create-token verbs make changes and can be relevant to persistence or lateral movement. bind assigns a pod to a specific node. approve configures a certificate signing request (CSR) which happens rarely. the authenticate verb authenticates a Kubernetes aPI request and can be relevant to credentialed access or privilege escalation.
user: The user or system that performed the action.
sourceIPs: The source IPs associated with the request.
userAgent: The user agent making the request.
objectRef: Metadata about the object being accessed or manipulated.
requestReceivedTimestamp: Timestamp for when the request was received.
stageTimestamp: Timestamp for when the stage completed.
responseStatus: Status of the request; success indicates a normal transaction and failure indicates an error. lots of failures here indicate either misconfiguration or possibly indication sof discovery, lateral movement, or privilege escalation activity.
annotations: contains authorization status. allow means the API call was permitted and forbid means it was unauthorized. lots of forbidden messages here are not nominal and mean either misconfiguration or possibly indications of discovery, lateral movement, or privilege escalation activity.

	For flow logs, ignore rows with a logstatus of NODATA because those are just errors and not threats. If there are interface-id and action fields, they are vpc flow log events. If there are fields whose names begin with k8s, they are Kubernetes events.

	Give a summary report on the data and explain what the nature of the activity is. Be verbose and identify fields you recognize. Explain each field that you recognize and what kind of data it contains. Suggest possible investigative directions."""
    
def get_response(prompt):

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": prompt},  
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
            #markdown_response += f"#### Choice {i + 1}\n"
            #markdown_response += f"- **Role**: {choice['message']['role']}\n"
            markdown_response += f"- **Content**: {choice['message']['content']}\n\n"
    else:
        markdown_response += "No choices found in the response."
    return markdown_response

# Function to parse the response and identify log types
def parse_log_types(response_text):
    log_types = []
    if "CloudTrail" in response_text:
        log_types.append("CloudTrail")
    if "Kubernetes" in response_text:
        log_types.append("Kubernetes")
    if "VPC Flow Logs" in response_text:
        log_types.append("VPC Flow Logs")
    return log_types

def run():  
    st.title("AI Assisted Data Investigation")

    prompt = """You are a security threat hunter and detection engineer examining some data that the user has provided. Identify the log type that has been attached.
	First, if the table data contains these fields, they are Cloudtrail events:
eventTime: the timestamp
eventSource: the AWS service which was used    
eventName: the name of the API call that was used
awsRegion: the name of the AWS region
sourceIPAddress: the source IP address of the caller
userAgent: the calling user agent    
readOnly: TRUE means the API call was only reading data or objects. FALSE means the API call made changes.
sessionCredentialFromConsole: TRUE means the API call took place interactively in the AWS console in a browser. FALSE means it was programmatic.
userIdentity.type: AssumeRole is a temporary role using an STS token. Root is the superuser for the account. AWSService means it came from an internal AWS service.
userIdentity.principalId: when this contains the word ‘instance” this identifies the EC2 instance that the API call came from.
userIdentity.arn: the user context which made the call.
userIdentity.sessionContext.attributes.mfaAuthenticated: FALSE means the user used multi factor authentication.
errorCode: if this field is not null, it contains the type of error which was returned. If it is null, there was no error.    
errorMessage:  if this field is not null, it contains the details of the error which was returned. If it is null, there was no error.    
response: details of the response to the API call.
request: details of the parameters in the API call that was made.

	If the table data contains these fields, they are VPC flow logs:

account-id: the AWS account number where the flow took place.
interface-id: the ENI (elastic network interface) that sent or received the flow.
srcaddr: the source IP address.
dstaddr: the destination IP address.
srcport: the source port.
dstport: the destination port.
protocol: the protocol number.
packets: the number of packets in the flow.    
bytes: the number of bytes in the flow.
start: the start time of the flow.
end: the end time of the flow.
action: the action taken by a security group. ACCEPT means the flow was permitted. REJECT means the flow was blocked by a security group.

	if the table data contains these fields, they are Kubernetes logs:
Kind: Specifies the type of the log entry (Event in this case).
apiVersion: Indicates the Kubernetes API version of the audit log.
Level: Indicates the verbosity or metadata level of the log entry.
auditID: Unique identifier for the audit event.
Stage: Represents the stage of the request lifecycle - a value of Panic would be a critical error.
requestURI: The URI for the Kubernetes API request.
verb: Specifies the action performed. watch, get and list verbs can be related to discovery and enumeration activity. delete and deletecollection can be relevant to defense evasion. create, update, connect, and create-token verbs make changes and can be relevant to persistence or lateral movement. bind assigns a pod to a specific node. approve configures a certificate signing request (CSR) which happens rarely. the authenticate verb authenticates a Kubernetes aPI request and can be relevant to credentialed access or privilege escalation.
user: The user or system that performed the action.
sourceIPs: The source IPs associated with the request.
userAgent: The user agent making the request.
objectRef: Metadata about the object being accessed or manipulated.
requestReceivedTimestamp: Timestamp for when the request was received.
stageTimestamp: Timestamp for when the stage completed.
responseStatus: Status of the request; success indicates a normal transaction and failure indicates an error. lots of failures here indicate either misconfiguration or possibly indication sof discovery, lateral movement, or privilege escalation activity.
annotations: contains authorization status. allow means the API call was permitted and forbid means it was unauthorized. lots of forbidden messages here are not nominal and mean either misconfiguration or possibly indications of discovery, lateral movement, or privilege escalation activity.
"""
    
    # File uploader for CSV
    uploaded_file = st.file_uploader("Upload your CSV file:", type=["csv"])
    csv_content = None
    if uploaded_file is not None:
        try:

            df = pd.read_csv(uploaded_file)
            st.markdown("### Uploaded Data (Showing First 25 Rows)")
            st.dataframe(df.head(5)) 
            csv_content = df.head(5).to_string(index=False)
        except Exception as e:
            st.error(f"Error loading CSV file: {e}")


    #include_csv = st.checkbox("Include table contents in the prompt")
    #st.markdown("### Enter Your Prompt Below")
    
    #prompt = st.text_input("Enter your prompt for Groq:")

    if st.button("Submit"):
        if prompt.strip():  
            if csv_content:
                prompt = f"{prompt}\n\n### Table Data (First 25 Rows):\n{csv_content}"
            
            #st.markdown("### Full Prompt Sent to API")
            #st.text(prompt)

            with st.spinner("Fetching answer from Groq..."):
                response = get_response(prompt)
            
            if response:
                #st.markdown("### API Response")
                markdown_response = format_response(response)
                st.markdown(markdown_response, unsafe_allow_html=True)
             # Parse and display identified log types
            response_text = markdown_response
            log_types = parse_log_types(response_text)
            if log_types:
                st.markdown("### Identified Log Types")
                for log_type in log_types:
                    link_page = log_type.lower().replace(" ", "_")
                    st.markdown(f"- [{log_type} Logs](/{link_page})")
            else:
                st.warning("No specific log type identified.")
        else:
            st.warning("Please enter a valid prompt.")


