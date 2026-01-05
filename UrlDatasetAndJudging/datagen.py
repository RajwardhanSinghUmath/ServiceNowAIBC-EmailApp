import os
import yaml
import json
import random
import sys
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generate import GenerateEmail
load_dotenv()

model_env_keys = ["OPENAI_MODEL_ONE", "OPENAI_MODEL_TWO", "OLLAMA_MODEL"]

print(f"Reading URLs from random_good_urls.txt")
with open("random_good_urls.txt", 'r') as f:
    urls = [line.strip() for line in f if line.strip()]
print(f"Found {len(urls)} URLs")

topics = ["Industry Trends", "Project Update", "New Resource", "Weekly Digest", "Strategic Partnership", "Product Launch", "Market Analysis", "Research Findings", "Technological Review", "Deployment Plan"]
personas = ["Product Manager", "CTO", "Research Lead", "Marketing Director", "Software Architect", "Data Scientist", "Project Coordinator", "Business Analyst"]
tones = ["Professional", "Formal", "Detailed", "Informative", "Persuasive", "Analytical"]
length_instruction = "approximately 400 words"

for env_key in model_env_keys:
    model_name = os.getenv(env_key)
    if not model_name:
        print(f"Skipping {env_key}: Not found in environment variables.")
        continue

    print(f"\n--- Initializing Generator for {model_name} ({env_key}) ---")
    try:
        generator = GenerateEmail(model_name)
    except Exception as e:
        print(f"Failed to initialize generator for {model_name}: {e}")
        continue

    safe_model_name = model_name.replace(":", "_").replace("/", "_").replace("\\", "_")
    output_filename = f"url_emails_{safe_model_name}.jsonl"
    print(f"Generating emails and saving to {output_filename}...")

    with open(output_filename, 'w', encoding='utf-8') as f_out:
        for i, url in enumerate(urls, 1):
            topic = random.choice(topics)
            persona = random.choice(personas)
            chosen_tone = random.choice(tones)
            print(f"[{i}/{len(urls)}] Generating for URL: {url} with {model_name}...")
            args = {
                "url": url,
                "topic": topic,
                "persona": persona,
                "length": length_instruction
            }
            try:
                raw_response = generator.generate("generate_with_url", args, tone=chosen_tone)
                clean_response = raw_response.strip()
                if "```json" in clean_response:
                    clean_response = clean_response.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_response:
                    clean_response = clean_response.split("```")[1].split("```")[0].strip()
                
                if not clean_response.startswith("{"):
                     start_idx = clean_response.find("{")
                     end_idx = clean_response.rfind("}")
                     if start_idx != -1 and end_idx != -1:
                         clean_response = clean_response[start_idx:end_idx+1]
                
                data = json.loads(clean_response)
                final_record = {
                    "id": i,
                    "sender": data.get("sender", f"sender{i}@example.com"),
                    "subject": data.get("subject", "No Subject"),
                    "content": data.get("content", ""),
                    "model": model_name
                }
                f_out.write(json.dumps(final_record) + "\n")
                f_out.flush()
            except Exception as e:
                print(f"Error generating for {url} with {model_name}: {e}")
