import os
import re
import yaml
import json
import sys
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generate import GenerateEmail
load_dotenv()
load_dotenv()

judge_model_name = os.getenv('OPENAI_MODEL_ONE')
judger = GenerateEmail(judge_model_name)
safe_judge_name = judge_model_name.replace(":", "_").replace("/", "_").replace("\\", "_")

model_env_keys = ["OPENAI_MODEL_ONE", "OPENAI_MODEL_TWO", "OLLAMA_MODEL"]

for env_key in model_env_keys:
    target_model_name = os.getenv(env_key)
    if not target_model_name:
        print(f"Skipping {env_key}: Not set in environment.")
        continue

    safe_target_name = target_model_name.replace(":", "_").replace("/", "_").replace("\\", "_")
    input_file = f"output_{safe_target_name}.jsonl"
    
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found. Skipping {target_model_name}.")
        continue

    output_file = f"output_judge_{safe_judge_name}_{safe_target_name}.jsonl"
    print(f"Judging {input_file} -> {output_file}...")

    try:
        num_lines = sum(1 for line in open(input_file, 'r', encoding='utf-8') if line.strip())
    except Exception:
        num_lines = 0

    with open(input_file, "r", encoding="utf-8") as f_in, \
         open(output_file, "w", encoding="utf-8") as f_out:
        for i, line in enumerate(f_in, 1):
            if not line.strip():
                continue
            
            print(f"[{i}/{num_lines}] Processing record...")
            data_item = json.loads(line)
            raw_output = judger.generate("judge_generation", data_item)
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw_output, re.DOTALL)
            if match:
                raw_output = match.group(1)
            try:
                score_data = json.loads(raw_output)
            except:
                score_data = {"error": "failed_to_parse", "raw": raw_output}
            result = {
                "topic": data_item.get("topic"),
                "persona": data_item.get("persona"),
                "evaluation": score_data,
                "target_model": target_model_name
            }
            f_out.write(json.dumps(result, ensure_ascii=False) + "\n")
            f_out.flush()
