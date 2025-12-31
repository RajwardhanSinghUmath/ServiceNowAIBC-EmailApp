import os
import yaml
import json
import random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Load prompts
with open("../prompts.yaml", "r") as f:
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
            messages=messages
        )
        return completion.choices[0].message.content
    
    def get_prompt(self, prompt_name, prompt_type='user', **kwargs):
        template = prompts[prompt_name][prompt_type]
        return template.format(**kwargs)
    
    def generate_email_with_url(self, url, topic, persona, tone, length):
        system_prompt = self.get_prompt('generate_with_url', 'system')
        user_prompt = self.get_prompt('generate_with_url', url=url, topic=topic, persona=persona, tone=tone, length=length)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        content = self._call_api(messages)
        return content

model_name = os.getenv('EVALUATOR_NAME', 'gpt-4o') 
generator = GenerateEmail(model_name)

print(f"Reading URLs from random_good_urls.txt")
with open("random_good_urls.txt", 'r') as f:
    urls = [line.strip() for line in f if line.strip()]

print(f"Found {len(urls)} URLs")

topics = ["Industry Trends", "Project Update", "New Resource", "Weekly Digest", "Strategic Partnership", "Product Launch", "Market Analysis", "Research Findings", "Technological Review", "Deployment Plan"]
personas = ["Product Manager", "CTO", "Research Lead", "Marketing Director", "Software Architect", "Data Scientist", "Project Coordinator", "Business Analyst"]
tones = ["Professional", "Formal", "Detailed", "Informative", "Persuasive", "Analytical"]
length_instruction = "approximately 400 words"

print(f"Generating emails and saving to url_emails.jsonl...")

with open("url_emails.jsonl", 'w', encoding='utf-8') as f_out:
    for i, url in enumerate(urls, 1):
        topic = random.choice(topics)
        persona = random.choice(personas)
        tone = random.choice(tones)
        
        print(f"[{i}/{len(urls)}] Generating for URL: {url}...")
        
        raw_response = generator.generate_email_with_url(url, topic, persona, tone, length_instruction)
        
        clean_response = raw_response.strip()
        if "```json" in clean_response:
            clean_response = clean_response.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_response:
            clean_response = clean_response.split("```")[1].split("```")[0].strip()
        
        data = json.loads(clean_response)

        final_record = {
            "id": i,
            "sender": data.get("sender", f"sender{i}@example.com"),
            "subject": data.get("subject", "No Subject"),
            "content": data.get("content", "")
        }
        
        f_out.write(json.dumps(final_record) + "\n")
        f_out.flush()
