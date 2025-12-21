import streamlit as st
import json
import requests
import os

from dotenv import load_dotenv
from generate import GenerateEmail

load_dotenv()

generator = GenerateEmail(os.getenv('DEPLOYMENT_NAME'))


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

if st.button("Elaborate"):
    st.write(generator.generate("lengthen",selected_email))
if st.button("Shorten"):
    st.write(generator.generate("shorten",selected_email))

option = st.selectbox("Change Tone", ["friendly", "sympathetic", "professional"])
if st.button("Change Tone"):
    st.write(generator.generate("tone",selected_email,option))

st.write("You selected ", option)

lengthen = []
shorten = []
tone = []

with open("datasets/lengthen.jsonl", "r") as f:
    for line in f:
        line = line.strip()
        lengthen.append(json.loads(line))

# st.dataframe(lengthen)

with open("datasets/shorten.jsonl", "r") as f:
    for line in f:
        line = line.strip()
        shorten.append(json.loads(line))

# st.dataframe(shorten)

with open("datasets/tone.jsonl", "r") as f:
    for line in f:
        line = line.strip()
        tone.append(json.loads(line))

# st.dataframe(tone)
