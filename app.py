import streamlit as st
import json
import requests
import os
from dotenv import load_dotenv
from generate import GenerateEmail
load_dotenv()
MODELS = {
    "OPENAI_MODEL_ONE": os.getenv("OPENAI_MODEL_ONE"),
    "OPENAI_MODEL_TWO": os.getenv("OPENAI_MODEL_TWO")
}
AVAILABLE_MODELS = {k: v for k, v in MODELS.items() if v}
st.set_page_config(page_title="AI Email Editor", page_icon="📧", layout="wide")
st.title("📧 AI Email Editing Tool")
st.sidebar.header("Configuration")
selected_model_key = st.sidebar.selectbox(
    "Select AI Model",
    options=list(AVAILABLE_MODELS.keys()),
    format_func=lambda x: f"{AVAILABLE_MODELS[x]}"
)
selected_model_name = AVAILABLE_MODELS[selected_model_key]
generator = GenerateEmail(selected_model_name)
evaluator = GenerateEmail(os.getenv('OPENAI_MODEL_ONE') or selected_model_name)
st.write(f"Using Model: **{selected_model_name}**")
st.write("Select an email record by ID and use AI to refine it.")
DATASET_OPTIONS = {
    "lengthen": "datasets/lengthen.jsonl",
    "shorten": "datasets/shorten.jsonl",
    "tone": "datasets/tone.jsonl",
    "url_emails": "UrlDatasetAndJudging/datasets/url_emails.jsonl"
}
option = st.sidebar.selectbox("Select Dataset", list(DATASET_OPTIONS.keys()))
emails = []
file_path = DATASET_OPTIONS[option]

if not os.path.exists(file_path):
    st.warning(f"File not found: {file_path}")
    st.stop()

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
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
    key=f"email_text_{option}_{selected_id}",
)
if "response_content" not in st.session_state:
    st.session_state.response_content = ""

on_selection = st.checkbox("Partial Edit Mode (Modify specific text only)")
selection_text = ""
partial_mode_type = "Contextual (Model merges)" 

if on_selection:
    partial_mode_type = st.radio(
        "Partial Edit Method:",
        ["Contextual (Model sees full mail, merges output)", "Fragment Only (Model sees only selection, manual merge)"]
    )
    selection_text = st.text_area("Paste the text fragment you want to modify:")

def process_email_action(action, **kwargs):
    input_data = selected_email.copy()
    
    input_data['content'] = email_text
    
    target_text = email_text
    is_partial = False

    if on_selection and selection_text.strip():
       target_text = selection_text
       is_partial = True
    
    if is_partial:
        if "Contextual" in partial_mode_type:
            action_key = f"{action}_contextual"
        else:
            action_key = f"{action}_fragment"
            
        input_data['selection'] = selection_text
    else:
        action_key = action

    if action == "tone":
        response = generator.generate(action_key, input_data, tone=kwargs.get('tone_option'))
    else:
        response = generator.generate(action_key, input_data)
        
    import re
    
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", response, re.DOTALL)
    if match:
        response = match.group(1)
        
    try:
        jsonresponse = json.loads(response)
    except json.JSONDecodeError:
        st.error(f"Failed to decode JSON from model response. Response was: {response}")
        return {}, ""
    
    final_content = jsonresponse.get("Content", "")
    
    if is_partial and "Fragment Only" in partial_mode_type:
        if target_text in email_text:
            final_content = email_text.replace(target_text, final_content)
        else:
            st.warning("Could not find the selected text in the main email body to replace. Showing raw result.")
            
    return jsonresponse, final_content
if st.button("Elaborate", use_container_width=True):
    jsonresponse, final_content = process_email_action("lengthen")
    st.write("**Lengthened Subject:** ")
    st.write(jsonresponse.get("Subject", "(Subject not modified)"))
    st.write("**Lengthened Salutation:** ")
    st.write(jsonresponse.get("Salutation", ""))
    st.write("**Lengthened Content: ** ")
    st.write(final_content)
    st.session_state.response_content = final_content
    st.write("**Lengthened Closing:** ")
    st.write(jsonresponse.get("Closing", ""))
if st.button("Shorten", use_container_width=True):
    jsonresponse, final_content = process_email_action("shorten")
    st.write("**Shortened Subject:** ")
    st.write(jsonresponse.get("Subject", "(Subject not modified)"))
    st.write("**Shortened Salutation:** ")
    st.write(jsonresponse.get("Salutation", ""))
    st.write("**Shortened Content:** ")
    st.write(final_content)
    st.session_state.response_content = final_content
    st.write("**Shortened Closing:** ")
    st.write(jsonresponse.get("Closing", ""))
if st.button("Shorten With URL", use_container_width=True):
    jsonresponse, final_content = process_email_action("shorten_with_url")
    st.write("**Shortened Subject:** ")
    st.write(jsonresponse.get("Subject", "(Subject not modified)"))
    st.write("**Shortened Salutation:** ")
    st.write(jsonresponse.get("Salutation", ""))
    st.write("**Shortened Content:** ")
    st.write(final_content)
    st.session_state.response_content = final_content
    st.write("**Shortened Closing:** ")
    st.write(jsonresponse.get("Closing", ""))
st.divider()
tone_option = st.selectbox("Change Tone", ["friendly", "sympathetic", "professional"])
if st.button("Change Tone", use_container_width=True):
    jsonresponse, final_content = process_email_action("tone", tone_option=tone_option)
    st.write("**Changed Tone Subject:** ")
    st.write(jsonresponse.get("Subject", "(Subject not modified)"))
    st.write("**Changed Tone Salutation:** ")
    st.write(jsonresponse.get("Salutation", ""))
    st.write("**Changed Tone Content: ** ")
    st.write(final_content)
    st.session_state.response_content = final_content
    st.write("**Changed Tone Closing:** ")
    st.write(jsonresponse.get("Closing", ""))
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
    response = evaluator.generate("robustness", {"content": selected_email["content"], "paraphrased_content": st.session_state.response_content})
    jsonresponse = json.loads(response)
    st.write("**Robustness Score:** ")
    st.write(jsonresponse["Score"])
    st.write("**Reasoning:** ")
    st.write(jsonresponse["Reasoning"])
