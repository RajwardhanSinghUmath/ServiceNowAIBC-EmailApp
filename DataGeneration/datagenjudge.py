import os
import re
import yaml
import json
import sys
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generate import GenerateEmail
load_dotenv()
judger = GenerateEmail(os.getenv('EVALUATOR_NAME'))
input_file = "output_gemma.jsonl"
output_file = "output_judge_4ogemma.jsonl"
num_lines = sum(1 for line in open(input_file, 'r', encoding='utf-8'))
with open(input_file, "r", encoding="utf-8") as f_in, \
     open(output_file, "a", encoding="utf-8") as f_out:
    for line in f_in:
        if not line.strip():
            continue
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
            "evaluation": score_data
        }
        f_out.write(json.dumps(result, ensure_ascii=False) + "\n")
        f_out.flush()
