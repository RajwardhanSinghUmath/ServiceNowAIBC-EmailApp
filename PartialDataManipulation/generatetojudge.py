import os
import json
import re
import sys
import random
from dotenv import load_dotenv

sys.path.append('..')
from generate import GenerateEmail

load_dotenv()

MODELS = [
    os.getenv("OLLAMA_MODEL"),
    os.getenv("OPENAI_MODEL_ONE"),
    os.getenv("OPENAI_MODEL_TWO")
]

MODELS = [m for m in MODELS if m]

DATASETS = [
    {
        "input_file": "datasets/lengthen.jsonl",
        "action": "lengthen_contextual",
        "variations": [None]
    },
    {
        "input_file": "datasets/shorten.jsonl",
        "action": "shorten_contextual",
        "variations": [None]
    },
    {
        "input_file": "datasets/tone.jsonl",
        "action": "tone_contextual",
        "variations": ["friendly", "sympathetic", "professional"]
    }
]

def process_dataset(generator, dataset_config, output_base_dir, model_name_file_safe):
    input_path = dataset_config["input_file"]
    action = dataset_config["action"]
    variations = dataset_config["variations"]

    if not os.path.exists(input_path):
        alt_path = os.path.join("..", input_path)
        if os.path.exists(alt_path):
            input_path = alt_path
        else:
            print(f"Skipping {input_path} (not found)")
            return

    print(f"Processing {input_path} with action '{action}'...")
    with open(input_path, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]

    for tone in variations:
        input_filename = os.path.basename(input_path).replace(".jsonl", "")
        if tone:
            out_filename = f"{action}_{tone}.jsonl"
            current_tone = tone
        else:
            out_filename = f"{action}.jsonl"
            current_tone = "professional" 

        model_output_dir = os.path.join(output_base_dir, model_name_file_safe)
        os.makedirs(model_output_dir, exist_ok=True)
        
        out_path = os.path.join(model_output_dir, out_filename)
        print(f"  Generating {out_filename} to {out_path}...")
        
        with open(out_path, "w", encoding="utf-8") as outfile:
            for i, record in enumerate(records):
                try:
                    content = record.get("content", "")
                    length = len(content)
                    if length > 10:
                        start_idx = random.randint(int(length * 0.25), int(length * 0.50))
                        end_idx = random.randint(int(length * 0.50), int(length * 0.75))
                        
                        if start_idx >= end_idx:
                             end_idx = min(start_idx + 5, length) 

                        text_before = content[:start_idx]
                        selection = content[start_idx:end_idx]
                        text_after = content[end_idx:]
                    else:
                        text_before = ""
                        selection = content
                        text_after = ""
                    
                    generate_args = record.copy()
                    generate_args["selection"] = selection
                    generate_args["content"] = content
                    
                    response_str = generator.generate(action, generate_args, tone=current_tone)
                    
                    match = re.search(r"```(?:json)?\s*(.*?)\s*```", response_str, re.DOTALL)
                    if match:
                        response_str = match.group(1)

                    generated = response_str
                    try:
                        response_json = json.loads(response_str)
                        generated = response_json.get("Content", response_str)
                    except json.JSONDecodeError:
                        pass

                    full_generated_email = generated
                    if "fragment" in action:
                        full_generated_email = text_before + generated + text_after

                    result = {
                        "original_id": record.get("id"),
                        "action": action,
                        "tone": current_tone,
                        "original_content": content,
                        "selection": selection,
                        "text_before_selection": text_before,
                        "text_after_selection": text_after,
                        "full_generated_email": full_generated_email,
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
        output_dir = "datasets" 
        
        print(f"Initializing generator with model: {model_id}")
        generator = GenerateEmail(model_id)
        
        for ds in DATASETS:
            process_dataset(generator, ds, output_dir, model_name_safe)
            
        print(f"Done for {model_id}!")
    except Exception as e:
        print(f"Critical Error for {model_id}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if not MODELS:
        print("No models found in environment variables.")
    else:
        for model in MODELS:
            run_for_model(model)
        print("\nAll models processed.")
