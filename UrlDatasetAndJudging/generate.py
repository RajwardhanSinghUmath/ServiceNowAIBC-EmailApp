from openai import OpenAI
from dotenv import load_dotenv
import os
import yaml
import json
import concurrent.futures
from pathlib import Path

load_dotenv()

# Load prompts
try:
    with open("../prompts.yaml", "r") as f:
        prompts = yaml.safe_load(f)
except FileNotFoundError:
    with open("prompts.yaml", "r") as f:
        prompts = yaml.safe_load(f)

class GenerateEmail():    
    def __init__(self, model: str):
        self.deployment_name = model
        # Use OLLAMA for gemma3, OPENAI for others
        if "gemma" in model.lower():
            self.client = OpenAI(
                base_url=os.getenv("OLLAMA_API_BASE"),
                api_key=os.getenv("OLLAMA_API_KEY"),
            )
        else:
            self.client = OpenAI(
                base_url=os.getenv("OPENAI_API_BASE"),
                api_key=os.getenv("OPENAI_API_KEY"),
            )

    def _call_api(self, messages):
        try:
            completion = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                response_format={"type": "json_object"}
            )
            return completion.choices[0].message.content
        except Exception as e:
            # Handle API errors gracefully
            print(f"API Error with model {self.deployment_name}: {e}")
            return None
    
    def get_prompt(self, prompt_name, prompt_type='user', **kwargs):
        template = prompts[prompt_name][prompt_type]
        return template.format(**kwargs)
    
    def send_prompt(self, user_prompt, system_msg):
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt}
        ]
        return self._call_api(messages)
    
    def generate(self, action, selected_email, **kwargs):
        # Merge email data with any additional kwargs (like tone)
        format_args = selected_email.copy()
        format_args.update(kwargs)
        
        system_prompt = self.get_prompt(action, prompt_type='system', **format_args)
        user_prompt = self.get_prompt(action, **format_args)
        return self.send_prompt(user_prompt, system_prompt)

# MODELS = ["gemma3:4b", "gpt-4.1", "gpt-4o-mini"]
MODELS = ["gpt-4.1", "gpt-4o-mini"]
DATASETS_DIR = "./datasets" 

# Define the tasks to generate
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
                # Attempt to parse json
                generated_json = json.loads(result)
            except json.JSONDecodeError:
                # Fallback if valid JSON isn't returned
                generated_json = {"raw_content": result}

            # Augment with metadata
            generated_json['original_id'] = original_id
            generated_json['task'] = task_name
            # Include original content for reference
            generated_json['original_content'] = email_data.get('content')
            generated_json['original_subject'] = email_data.get('subject')

            return json.dumps(generated_json)
        else:
            return None
    except Exception as e:
        print(f"Error processing ID {original_id} for task {task_name}: {e}")
        return None

def main():
    input_file = "url_emails.jsonl"
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found locally.")
        return

    # Ensure dataset directory exists
    base_output_dir = Path(DATASETS_DIR)
    
    # Read source emails
    print(f"Reading {input_file}...")
    with open(input_file, "r", encoding="utf-8") as f:
        email_lines = [line.strip() for line in f if line.strip()]
    
    total_emails = len(email_lines)
    print(f"Loaded {total_emails} emails.")

    # Process each model
    for model in MODELS:
        print(f"\nModel: {model}")
        generator = GenerateEmail(model)
        
        # Create model directory (sanitize colons for Windows)
        safe_model_name = model.replace(":", "_")
        model_dir = base_output_dir / safe_model_name
        if not base_output_dir.exists():
            # If ../datasets doesn't exist, try local `datasets` or create one
            if os.path.exists("datasets"):
                base_output_dir = Path("datasets")
                model_dir = base_output_dir / model
            else:
                # Default to creating what we defined if parent logic matches
                pass
                
        model_dir.mkdir(parents=True, exist_ok=True)
        print(f"Output directory: {model_dir}")

        for task_name, config in TASKS.items():
            output_filename = config["filename"]
            output_path = model_dir / output_filename
            
            print(f"  Generating task '{task_name}' -> {output_filename}")
            
            # Use Multithreading
            # We assume the generator instance is thread-safe enough for simple API calls (stateless client usage)
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for line in email_lines:
                    email_data = json.loads(line)
                    original_id = email_data.get('id')
                    
                    futures.append(
                        executor.submit(
                            process_single_email,
                            generator,
                            task_name,
                            config,
                            email_data,
                            original_id
                        )
                    )
                
                # Collect results
                with open(output_path, "w", encoding="utf-8") as f_out:
                    count = 0
                    for future in concurrent.futures.as_completed(futures):
                        res_str = future.result()
                        if res_str:
                            f_out.write(res_str + "\n")
                            f_out.flush()
                            count += 1
                        
                        # Optional: Progress indicator
                        if count % 10 == 0:
                            print(f"    {count}/{total_emails}", end='\r')
                    print(f"    {count}/{total_emails} completed.")

    print("\nAll generation tasks completed.")

if __name__ == "__main__":
    main()
