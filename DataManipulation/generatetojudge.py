import os
import json
import re
import sys
sys.path.append('..')
from generate import GenerateEmail
load_dotenv()
MODELS = [
    os.getenv("OLLAMA_MODEL"),
    os.getenv("OPENAI_MODEL_ONE"),
    os.getenv("OPENAI_MODEL_TWO")
]
DATASETS = [
    {
        "input_file": "../datasets/lengthen.jsonl",
        "action": "lengthen",
        "variations": [None]        
    },
    {
        "input_file": "../datasets/shorten.jsonl",
        "action": "shorten",
        "variations": [None]
    },
    {
        "input_file": "../datasets/tone.jsonl",
        "action": "tone",
        "variations": ["friendly", "sympathetic", "professional"]
    }
]
def process_dataset(generator, dataset_config, output_dir, model_name_file_safe):
    input_path = dataset_config["input_file"]
    action = dataset_config["action"]
    variations = dataset_config["variations"]
    if not os.path.exists(input_path):
        print(f"Skipping {input_path} (not found)")
        return
    print(f"Processing {input_path} with action '{action}'...")
    with open(input_path, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]
    for tone in variations:
        base_name = os.path.basename(input_path).replace(".jsonl", "")
        if tone:
            out_filename = f"{base_name}_{tone}.jsonl"
            current_tone = tone
        else:
            out_filename = f"{base_name}.jsonl"
            current_tone = "professional" 
        out_path = os.path.join(output_dir, out_filename)
        print(f"  Generating {out_filename}...")
        with open(out_path, "w", encoding="utf-8") as outfile:
            for i, record in enumerate(records):
                try:
                    response_str = generator.generate(action, record, tone=current_tone)
                    match = re.search(r"```(?:json)?\s*(.*?)\s*```", response_str, re.DOTALL)
                    if match:
                        response_str = match.group(1)
                    try:
                        response_json = json.loads(response_str)
                        generated_content = response_json.get("Content", response_str)
                    except json.JSONDecodeError:
                        generated_content = response_str
                    result = {
                        "original_id": record.get("id"),
                        "action": action,
                        "tone": current_tone,
                        "original_content": record.get("content"),
                        "generated_content": generated_content,
                        "model": model_name_file_safe
                    }
                    outfile.write(json.dumps(result) + "\n")
                    outfile.flush()
                except Exception as e:
                    print(f"    Error processing ID {record.get('id')}: {e}")
def run_for_model(model_id):
    if not model_id:
        return
    print(f"\n--- Starting generation for model: {model_id} ---")
    try:
        model_name_safe = model_id.replace(":", "_")
        output_dir = f"../datasets/{model_name_safe}"
        os.makedirs(output_dir, exist_ok=True)
        print(f"Initializing generator with model: {model_id}")
        generator = GenerateEmail(model_id)
        for ds in DATASETS:
            process_dataset(generator, ds, output_dir, model_name_safe)
        print(f"Done for {model_id}!")
    except Exception as e:
        print(f"Critical Error for {model_id}: {e}")
for model in MODELS:
    run_for_model(model)
print("\nAll models processed.")
