import os
import json
from dotenv import load_dotenv
load_dotenv()
MODELS = [
    os.getenv("OLLAMA_MODEL"),
    os.getenv("OPENAI_MODEL_ONE"),
    os.getenv("OPENAI_MODEL_TWO")
]
DATASETS_DIR = "../datasets"
FILES_TO_ANALYZE = {
    "lengthen": ["lengthen.jsonl"],
    "shorten": ["shorten.jsonl"],
    "tone_friendly": ["tone_friendly.jsonl"],
    "tone_professional": ["tone_professional.jsonl"],
    "tone_sympathetic": ["tone_sympathetic.jsonl"],
}
def calculate_word_count(text):
    if not isinstance(text, str):
        return 0
    return len(text.split())
def process_judged_file(file_path):
    stats = {
        "faithfulness": [],
        "completeness": [],
        "robustness": [],
        "compression_ratio": [],
        "expansion_ratio": []
    }
    if not os.path.exists(file_path):
        return stats
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                judgement = record.get("judgement", {})
                for metric in ["faithfulness", "completeness", "robustness"]:
                    score = judgement.get(metric, {}).get("score")
                    if score is not None:
                        try:
                            stats[metric].append(float(score))
                        except (ValueError, TypeError):
                            pass
                original_content = record.get("original_content", "")
                generated_content = record.get("generated_content", "")
                if generated_content.strip().startswith("```json"):
                     pass
                orig_len = calculate_word_count(original_content)
                gen_len = calculate_word_count(generated_content) 
                if isinstance(generated_content, str) and generated_content.strip().startswith("{"):
                     try:
                         data = json.loads(generated_content)
                         if isinstance(data, dict):
                             generated_content = data.get("Content", generated_content)
                     except:
                         pass
                gen_len = calculate_word_count(generated_content)
                if orig_len > 0:
                    ratio = gen_len / orig_len
                    stats["expansion_ratio"].append(ratio)
                    stats["compression_ratio"].append(ratio) 
            except json.JSONDecodeError:
                continue
    return stats
results = {}
tone_ratios = {"overall": []}
def avg(lst):
    return sum(lst) / len(lst) if lst else 0
for model in MODELS:
    results[model] = {}
    tone_ratios[model] = []
    safe_model_name = model.replace(":", "_") if model else ""
    judged_dir = os.path.join(DATASETS_DIR, safe_model_name, "judged")
    for task, files in FILES_TO_ANALYZE.items():
        task_stats = {
            "faithfulness": [],
            "completeness": [],
            "robustness": [],
            "ratio": [] 
        }
        for fname in files:
            fpath = os.path.join(judged_dir, fname)
            file_stats = process_judged_file(fpath)
            task_stats["faithfulness"].extend(file_stats["faithfulness"])
            task_stats["completeness"].extend(file_stats["completeness"])
            task_stats["robustness"].extend(file_stats["robustness"])
            if task == "shorten":
                    task_stats["ratio"].extend(file_stats["compression_ratio"])
            elif task == "lengthen":
                    task_stats["ratio"].extend(file_stats["expansion_ratio"])
            else:
                    task_stats["ratio"].extend(file_stats["expansion_ratio"])
                    tone_ratios[model].extend(file_stats["expansion_ratio"])
                    tone_ratios["overall"].extend(file_stats["expansion_ratio"])
        results[model][task] = {
            "avg_faithfulness": avg(task_stats["faithfulness"]),
            "avg_completeness": avg(task_stats["completeness"]),
            "avg_robustness": avg(task_stats["robustness"]),
            "avg_len_ratio": avg(task_stats["ratio"])
        }
print(f"{'Model':<15} {'Task':<20} {'Faithfulness':<15} {'Completeness':<15} {'Robustness':<15} {'Len Ratio (Gen/Orig)':<20}")
print("-" * 100)
for model, tasks in results.items():
    if not tasks: continue
    for task, metrics in tasks.items():
        print(f"{model:<15} {task:<20} {metrics['avg_faithfulness']:.2f}{'':<11} {metrics['avg_completeness']:.2f}{'':<11} {metrics['avg_robustness']:.2f}{'':<11} {metrics['avg_len_ratio']:.2f}")
print("-" * 100)
print("Tone Change Task - Average Length Ratio")
print("-" * 100)
for model in MODELS:
    if model:
        print(f"{model:<15} {'Tone Avg':<20} {avg(tone_ratios[model]):.2f}")
print(f"{'Overall':<15} {'Tone Avg':<20} {avg(tone_ratios['overall']):.2f}")
