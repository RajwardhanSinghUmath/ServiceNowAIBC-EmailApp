import os
import json
import re
import yaml
import concurrent.futures
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Load prompts
with open("prompts.yaml", "r") as f:
    prompts = yaml.safe_load(f)

class GenerateEmail():    
    def __init__(self, model: str):
        if "gemma" in model.lower():
            base_url = os.getenv("OLLAMA_API_BASE")
            api_key = os.getenv("OLLAMA_API_KEY")
        else:
            base_url = os.getenv("OPENAI_API_BASE")
            api_key = os.getenv("OPENAI_API_KEY")

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
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
    
    def send_prompt(self, user_prompt: str, system_msg="You are a helpful assistant."):
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt}
        ]
        return self._call_api(messages)
    
    def generate(self, action: str, selected_email, tone="professional"):
        args = selected_email.copy() # Use copy to avoid modifying original info if passed by ref
        args["tone"] = tone
        system_prompt = self.get_prompt(action, prompt_type='system', **args)
        user_prompt = self.get_prompt(action, **args)
        return self.send_prompt(user_prompt, system_prompt)

EVALUATOR_NAME = os.getenv("EVALUATOR_NAME")
if not EVALUATOR_NAME:
    print("Error: EVALUATOR_NAME not set in .env")
    exit(1)

MODELS = ["gemma3_4b", "gpt-4.1", "gpt-4o-mini"]
FILES_TO_JUDGE = [
    "lengthen.jsonl",
    "shorten.jsonl", 
    "tone_friendly.jsonl",
    "tone_professional.jsonl",
    "tone_sympathetic.jsonl"
]

def clean_json_string(s):
    """
    Attempts to clean up a string that might contain Markdown code blocks
    so it can be parsed as JSON.
    """
    if not isinstance(s, str):
        return s
    # Remove ```json ... ``` or similar
    s = s.strip()
    match = re.search(r"```(?:json)?\s*(.*)\s*```", s, re.DOTALL)
    if match:
        s = match.group(1)
    return s.strip()

def extract_email_content(generated_output):
    """
    Parses the generated output (which is expected to be a JSON string)
    and extracts the 'Content' field.
    """
    cleaned = clean_json_string(generated_output)
    try:
        data = json.loads(cleaned)
        # If it's a dict, look for 'Content'
        if isinstance(data, dict):
            return data.get("Content", cleaned)
        return cleaned
    except json.JSONDecodeError:
        # If not valid JSON, just return the raw string
        return cleaned

def evaluate_record(evaluator, content, paraphrased_content):
    """
    Runs the three evaluation metrics: faithfulness, completeness, robustness.
    Returns a dict with scores and reasonings.
    """
    metrics = ["faithfulness", "completeness", "robustness"]
    results = {}
    
    for metric in metrics:
        try:
            # The prompts expect: actual mail: {content}, paraphrased mail: {paraphrased_content}
            response_str = evaluator.generate(
                metric, 
                {"content": content, "paraphrased_content": paraphrased_content}
            )
            
            # Parse the evaluator's JSON response
            cleaned_response = clean_json_string(response_str)
            response_json = json.loads(cleaned_response)
            
            results[metric] = {
                "score": response_json.get("Score"),
                "reasoning": response_json.get("Reasoning")
            }
        except Exception as e:
            print(f"Error evaluating {metric}: {e}")
            results[metric] = {"score": None, "reasoning": f"Error: {e}"}
            
    return results

def process_single_line(evaluator, line):
    """
    Helper function to process a single line (record) from the input file.
    Designed to be used with ThreadPoolExecutor.
    """
    line = line.strip()
    if not line:
        return None
        
    try:
        record = json.loads(line)
        original_content = record.get("original_content", "")
        generated_raw = record.get("generated_content", "")
        
        # Extract the actual email body text from the generation result
        paraphrased_content = extract_email_content(generated_raw)
        
        # Run evaluations
        eval_results = evaluate_record(evaluator, original_content, paraphrased_content)
        
        # Merge results into the record
        record["judgement"] = eval_results
        
        return json.dumps(record)
        
    except json.JSONDecodeError:
        print("    Failed to decode line in input file.")
        return None
    except Exception as e:
        print(f"    Error processing record: {e}")
        return None

def process_file(evaluator, model_dir, file_name, judged_dir):
    input_path = os.path.join(model_dir, file_name)
    if not os.path.exists(input_path):
        print(f"  Skipping {file_name} (not found)")
        return

    output_path = os.path.join(judged_dir, file_name)
    print(f"  Judging {file_name} -> {output_path}")

    # Read all lines first
    try:
        with open(input_path, "r", encoding="utf-8") as f_in:
            lines = f_in.readlines()
    except Exception as e:
        print(f"    Error reading file {input_path}: {e}")
        return

    # Use ThreadPoolExecutor to process lines in parallel
    # max_workers=10 is a reasonable starting point for I/O bound tasks
    with open(output_path, "w", encoding="utf-8") as f_out:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # We map the process_single_line function over the lines.
            # Lambda is used to pass the 'evaluator' argument.
            # map preserves the order of results corresponding to the input iterable.
            results = executor.map(lambda l: process_single_line(evaluator, l), lines)
            
            for res in results:
                if res:
                    f_out.write(res + "\n")
                    f_out.flush()

def main():
    print(f"Initializing Evaluator: {EVALUATOR_NAME}")
    evaluator = GenerateEmail(EVALUATOR_NAME)
    
    base_datasets_dir = "datasets"
    
    for model_name in MODELS:
        print(f"Processing model: {model_name}")
        model_dir = os.path.join(base_datasets_dir, model_name)
        
        if not os.path.isdir(model_dir):
            print(f"Directory not found for model {model_name}, skipping.")
            continue
            
        # Create 'judged' subfolder inside the model folder
        judged_dir = os.path.join(model_dir, "judged")
        os.makedirs(judged_dir, exist_ok=True)
        
        for fname in FILES_TO_JUDGE:
            process_file(evaluator, model_dir, fname, judged_dir)
            
    print("All judging complete.")

if __name__ == "__main__":
    main()
