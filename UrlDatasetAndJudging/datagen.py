import os
import yaml
import json
import random
import sys
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generate import GenerateEmail
load_dotenv()
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
        chosen_tone = random.choice(tones)
        print(f"[{i}/{len(urls)}] Generating for URL: {url}...")
        args = {
            "url": url,
            "topic": topic,
            "persona": persona,
            "length": length_instruction
        }
        raw_response = generator.generate("generate_with_url", args, tone=chosen_tone)
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
