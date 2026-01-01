import os
import json
from dotenv import load_dotenv
from generate import GenerateEmail

load_dotenv()

MODEL_ID = os.getenv("OLLAMA_MODEL_NAME")
if not MODEL_ID:
    print("Error: OLLAMA_MODEL not set in .env")
    exit(1)

MODEL_NAME = MODEL_ID.replace(":", "_") 
OUTPUT_DIR = os.path.join("datasets", MODEL_NAME)
os.makedirs(OUTPUT_DIR, exist_ok=True)

DATASETS = [
    {
        "input_file": "datasets/lengthen.jsonl",
        "action": "lengthen",
        "variations": [None]        
    },
    {
        "input_file": "datasets/shorten.jsonl",
        "action": "shorten",
        "variations": [None]
    },
    {
        "input_file": "datasets/tone.jsonl",
        "action": "tone",
        "variations": ["friendly", "sympathetic", "professional"]
    }
]

def process_dataset(generator, dataset_config):
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
            
        out_path = os.path.join(OUTPUT_DIR, out_filename)
        print(f"  Generating {out_filename}...")
        
        with open(out_path, "w", encoding="utf-8") as outfile:
            for i, record in enumerate(records):
                try:
                    response_str = generator.generate(action, record, tone=current_tone)
                    
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
                        "model": MODEL_NAME
                    }
                    outfile.write(json.dumps(result) + "\n")
                    outfile.flush()
                    
                except Exception as e:
                    print(f"    Error processing ID {record.get('id')}: {e}")

def main():
    try:
        print(f"Initializing generator with model: {MODEL_ID}")
        generator = GenerateEmail(MODEL_ID)
        
        for ds in DATASETS:
            process_dataset(generator, ds)
            
        print("Done!")
        
    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    main()
