import streamlit as st
import json
import requests
import os

from dotenv import load_dotenv
from generate import GenerateEmail

load_dotenv()

generator = GenerateEmail(os.getenv('DEPLOYMENT_NAME'))
evaluator = GenerateEmail(os.getenv('EVALUATOR_NAME'))


st.set_page_config(page_title="AI Email Editor", page_icon="📧", layout="wide")


st.title("📧 AI Email Editing Tool")
st.write("Select an email record by ID and use AI to refine it.")
option = st.sidebar.selectbox("Select Dataset", ["lengthen", "shorten", "tone"])

emails = []
with open(f"datasets/{option}.jsonl", "r") as f:
    for line in f:
        line = line.strip()
        emails.append(json.loads(line))

if not emails:
    st.warning("No emails found in your JSONL file.")
    st.stop()

email_ids = [email["id"] for email in emails]

selected_id = st.sidebar.selectbox(
    "📂 Select Email ID",
    options=email_ids,
    index=0
)

selected_email = next(
    (email for email in emails if email["id"] == selected_id),
    None
)

if not selected_email:
    st.error(f"No email found with ID {selected_id}.")
    st.stop()

st.markdown(f"### ✉️ Email ID: `{selected_id}`")
st.markdown(f"**From:** {selected_email.get('sender', '(unknown)')}")
st.markdown(f"**Subject:** {selected_email.get('subject', '(no subject)')}")

email_text = st.text_area(
    "Email Content",
    value=selected_email.get("content", ""),
    height=250,
    key=f"email_text_{selected_id}",
)
if "response_content" not in st.session_state:
    st.session_state.response_content = ""

if st.button("Elaborate", use_container_width=True):
    response = generator.generate("lengthen", selected_email)
    jsonresponse = json.loads(response)
    st.write("**Lengthened Subject:** ")
    st.write(jsonresponse["Subject"])
    st.write("**Lengthened Salutation:** ")
    st.write(jsonresponse["Salutation"])
    st.write("**Lengthened Content:** ")
    st.write(jsonresponse["Content"])
    st.session_state.response_content = jsonresponse["Content"]
    st.write("**Lengthened Closing:** ")
    st.write(jsonresponse["Closing"])

if st.button("Shorten", use_container_width=True):
    response = generator.generate("shorten", selected_email)
    jsonresponse = json.loads(response)
    st.write("**Shortened Subject:** ")
    st.write(jsonresponse["Subject"])
    st.write("**Shortened Salutation:** ")
    st.write(jsonresponse["Salutation"])
    st.write("**Shortened Content:** ")
    st.session_state.response_content = jsonresponse["Content"]
    st.write(jsonresponse["Content"])
    st.write("**Shortened Closing:** ")
    st.write(jsonresponse["Closing"])

st.divider()

tone_option = st.selectbox("Change Tone", ["friendly", "sympathetic", "professional"])
if st.button("Change Tone", use_container_width=True):
    response = generator.generate("tone", selected_email, tone_option)
    jsonresponse = json.loads(response)
    st.write("**Changed Subject:** ")
    st.write(jsonresponse["Subject"])
    st.write("**Changed Salutation:** ")
    st.write(jsonresponse["Salutation"])
    st.write("**Changed Content:** ")
    st.write(jsonresponse["Content"])
    st.session_state.response_content = jsonresponse["Content"]
    st.write("**Changed Closing:** ")
    st.write(jsonresponse["Closing"])

st.divider()

if st.button("Evaluate", use_container_width=True):
    response = evaluator.generate("faithfulness", {"content": selected_email["content"], "paraphrased_content": st.session_state.response_content})
    st.write("**Changed Content:** ")
    st.write(st.session_state.response_content)
    jsonresponse = json.loads(response)
    st.write("**Faithfullness Score:** ")
    st.write(jsonresponse["Score"])
    st.write("**Reasoning:** ")
    st.write(jsonresponse["Reasoning"])
    response = evaluator.generate("completeness", {"content": selected_email["content"], "paraphrased_content": st.session_state.response_content})
    jsonresponse = json.loads(response)
    st.write("**Completeness Score:** ")
    st.write(jsonresponse["Score"])
    st.write("**Reasoning:** ")
    st.write(jsonresponse["Reasoning"])
lengthen = []
with open("datasets/lengthen.jsonl", "r") as f:
    for line in f:
        line = line.strip()
        lengthen.append(json.loads(line))

shorten = []
with open("datasets/shorten.jsonl", "r") as f:
    for line in f:
        line = line.strip()
        shorten.append(json.loads(line))

tone = []
with open("datasets/tone.jsonl", "r") as f:
    for line in f:
        line = line.strip()
        tone.append(json.loads(line))
