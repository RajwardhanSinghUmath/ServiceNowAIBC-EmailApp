from openai import OpenAI
from dotenv import load_dotenv
import os
import yaml
import json

load_dotenv()

try:
    with open("../prompts.yaml", "r") as f:
        prompts = yaml.safe_load(f)
except FileNotFoundError:
    with open("prompts.yaml", "r") as f:
        prompts = yaml.safe_load(f)

class GenerateEmail():    
    def __init__(self, model: str):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_API_BASE"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.deployment_name = model

    def _call_api(self, messages):
        completion = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages,
            response_format={"type": "json_object"}
        )
        return completion.choices[0].message.content
    
    def get_prompt(self, prompt_name, prompt_type='user', **kwargs):
        template = prompts[prompt_name][prompt_type]
        return template.format(**kwargs)
    
    def send_prompt(self, user_prompt, system_msg):
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt}
        ]
        return self._call_api(messages)
    
    def generate(self, action, selected_email):
        system_prompt = self.get_prompt(action, prompt_type='system', **selected_email)
        user_prompt = self.get_prompt(action, **selected_email)
        return self.send_prompt(user_prompt, system_prompt)

model_name = os.getenv('EVALUATOR_NAME', 'gpt-4o')
generator = GenerateEmail(model_name)

print("Starting explicit URL preservation shortening process...")

with open("url_emails.jsonl", "r", encoding="utf-8") as f_in, \
     open("shortened_explicit_url_emails.jsonl", "w", encoding="utf-8") as f_out:
    
    lines = f_in.readlines()
    print(f"Found {len(lines)} emails to process.")
    
    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue
            
        email_data = json.loads(line)
        original_id = email_data.get('id')
        
        print(f"[{i}/{len(lines)}] Shortening (preserving URL) ID {original_id}...")
        
        try:
            result = generator.generate("shorten_with_url", email_data)
            
            shortened_json = json.loads(result)
            shortened_json['original_id'] = original_id
            
            f_out.write(json.dumps(shortened_json) + "\n")
            f_out.flush()
        except Exception as e:
            print(f"Error processing ID {original_id}: {e}")

print("Done. Saved to shortened_explicit_url_emails.jsonl")