import os
import json
import re
import yaml
from dotenv import load_dotenv
import sys
sys.path.append('..')
from generate import GenerateEmail
load_dotenv()
EVALUATOR_NAME = os.getenv("EVALUATOR_NAME")
if not EVALUATOR_NAME:
    print("Error: EVALUATOR_NAME not set in .env")
    exit(1)
MODELS = [
    os.getenv("OLLAMA_MODEL"),
    os.getenv("OPENAI_MODEL_ONE"),
    os.getenv("OPENAI_MODEL_TWO")
]
FILES_TO_JUDGE = [
    "lengthen.jsonl",
    "shorten.jsonl", 
    "tone_friendly.jsonl",
    "tone_professional.jsonl",
    "tone_sympathetic.jsonl"
]
def clean_json_string(s):
    if not isinstance(s, str):
        return s
    s = s.strip()
    match = re.search(r"```(?:json)?\s*(.*)\s*```", s, re.DOTALL)
    if match:
        s = match.group(1)
    return s.strip()
def extract_email_content(generated_output):
    cleaned = clean_json_string(generated_output)
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data.get("Content", cleaned)
        return cleaned
    except json.JSONDecodeError:
        return cleaned
def evaluate_record(evaluator, content, paraphrased_content):
    metrics = ["faithfulness", "completeness", "robustness"]
    results = {}
    for metric in metrics:
        try:
            response_str = evaluator.generate(
                metric, 
                {"content": content, "paraphrased_content": paraphrased_content}
            )
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
    line = line.strip()
    if not line:
        return None
    try:
        record = json.loads(line)
        original_content = record.get("original_content", "")
        generated_raw = record.get("generated_content", "")
        paraphrased_content = extract_email_content(generated_raw)
        eval_results = evaluate_record(evaluator, original_content, paraphrased_content)
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
    try:
        with open(input_path, "r", encoding="utf-8") as f_in:
            lines = f_in.readlines()
    except Exception as e:
        print(f"    Error reading file {input_path}: {e}")
        return
    with open(output_path, "w", encoding="utf-8") as f_out:
        for line in lines:
            res = process_single_line(evaluator, line)
            if res:
                f_out.write(res + "\n")
                f_out.flush()
print(f"Initializing Evaluator: {EVALUATOR_NAME}")
evaluator = GenerateEmail(EVALUATOR_NAME)
base_datasets_dir = "../datasets"
for model_name in MODELS:
    if not model_name: continue
    print(f"Processing model: {model_name}")
    safe_model_name = model_name.replace(":", "_")
    model_dir = os.path.join(base_datasets_dir, safe_model_name)
    if not os.path.isdir(model_dir):
        print(f"Directory not found for model {model_name}, skipping.")
        continue
    judged_dir = os.path.join(model_dir, "judged")
    os.makedirs(judged_dir, exist_ok=True)
    for fname in FILES_TO_JUDGE:
        process_file(evaluator, model_dir, fname, judged_dir)
print("All judging complete.")
