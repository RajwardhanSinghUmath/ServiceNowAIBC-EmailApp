import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
import sys
load_dotenv()
sys.path.append('..')
from generate import GenerateEmail
MODELS = [
    os.getenv("OLLAMA_MODEL"),
    os.getenv("OPENAI_MODEL_ONE"),
    os.getenv("OPENAI_MODEL_TWO")
]
DATASETS_DIR = "../datasets" 
TASKS = {
    "shorten": {
        "prompt_key": "shorten", 
        "kwargs": {}, 
        "filename": "shorten.jsonl"
    },
    "shorten_with_url": {
        "prompt_key": "shorten_with_url", 
        "kwargs": {}, 
        "filename": "shorten_with_url.jsonl"
    }
}
def process_single_email(generator, task_name, task_config, email_data, original_id):
    try:
        prompt_key = task_config["prompt_key"]
        extra_kwargs = task_config["kwargs"]
        result = generator.generate(prompt_key, email_data, **extra_kwargs)
        if result:
            try:
                match = re.search(r"```(?:json)?\s*(.*?)\s*```", result, re.DOTALL)
                if match:
                    result = match.group(1)
                generated_json = json.loads(result)
            except json.JSONDecodeError:
                generated_json = {"raw_content": result}
            generated_json['original_id'] = original_id
            generated_json['task'] = task_name
            generated_json['original_content'] = email_data.get('content')
            generated_json['original_subject'] = email_data.get('subject')
            return json.dumps(generated_json)
        else:
            return None
    except Exception as e:
        print(f"Error processing ID {original_id} for task {task_name}: {e}")
        return None
input_file = "url_emails.jsonl"
if not os.path.exists(input_file):
    print(f"Input file {input_file} not found locally.")
    exit()
base_output_dir = Path(DATASETS_DIR)
print(f"Reading {input_file}...")
with open(input_file, "r", encoding="utf-8") as f:
    email_lines = [line.strip() for line in f if line.strip()]
total_emails = len(email_lines)
print(f"Loaded {total_emails} emails.")
for model in MODELS:
    print(f"\nModel: {model}")
    generator = GenerateEmail(model)
    safe_model_name = model.replace(":", "_")
    model_dir = base_output_dir / safe_model_name
    if not base_output_dir.exists():
        if os.path.exists("datasets"):
            base_output_dir = Path("datasets")
            model_dir = base_output_dir / model
        else:
            pass
    model_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {model_dir}")
    for task_name, config in TASKS.items():
        output_filename = config["filename"]
        output_path = model_dir / output_filename
        print(f"  Generating task '{task_name}' -> {output_filename}")
        with open(output_path, "w", encoding="utf-8") as f_out:
            count = 0
            for line in email_lines:
                email_data = json.loads(line)
                original_id = email_data.get('id')
                res_str = process_single_email(
                    generator,
                    task_name,
                    config,
                    email_data,
                    original_id
                )
                if res_str:
                    f_out.write(res_str + "\n")
                    f_out.flush()
                    count += 1
                if count % 10 == 0:
                    print(f"    {count}/{total_emails}", end='\r')
            print(f"    {count}/{total_emails} completed.")
print("\nAll generation tasks completed.")
