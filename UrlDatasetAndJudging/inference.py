import os
import json
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv
load_dotenv()
MODELS = [
    os.getenv("OLLAMA_MODEL"),
    os.getenv("OPENAI_MODEL_ONE"),
    os.getenv("OPENAI_MODEL_TWO")
]
DATASETS_DIR = "./datasets"
def load_originals():
    """Load the original emails and target URLs."""
    try:
        with open(os.path.join(DATASETS_DIR, "random_good_urls.txt"), "r") as f:
            target_urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        target_urls = []
        print("Warning: random_good_urls.txt not found.")
    original_emails = {}
    url_emails_path = os.path.join(DATASETS_DIR, "url_emails.jsonl")
    if os.path.exists(url_emails_path):
        with open(url_emails_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    original_emails[data['id']] = data.get('content', '')
    else:
        print("Warning: url_emails.jsonl not found.")
    return target_urls, original_emails
def load_generated(file_path):
    """Load generated emails from a specific file."""
    emails = {}
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        oid = data.get('original_id')
                        content = data.get('Content') or data.get('content') or ""
                        if oid:
                            emails[oid] = content
                    except json.JSONDecodeError:
                        pass
    return emails
def calculate_metrics(target_urls, original_emails, generated_emails):
    """Calculate extraction and length metrics."""
    total_gen = len(generated_emails)
    if total_gen == 0:
        return {
            "success_rate": 0,
            "retention_acc": 0,
            "avg_len_ratio": 0
        }
    url_found_count = 0
    valid_pairs = 0
    retained_count = 0
    ratios = []
    id_to_url = {i+1: url for i, url in enumerate(target_urls)}
    for eid, content in generated_emails.items():
        if eid not in original_emails:
            continue
        target_url = id_to_url.get(eid)
        if not target_url:
            continue
        if target_url in content:
            url_found_count += 1
        orig_content = original_emails[eid]
        if target_url in orig_content:
            valid_pairs += 1
            if target_url in content:
                retained_count += 1
        orig_words = len(orig_content.split())
        gen_words = len(content.split())
        if orig_words > 0:
            ratios.append(gen_words / orig_words)
    success_rate = (url_found_count / total_gen * 100) if total_gen > 0 else 0
    retention_acc = (retained_count / valid_pairs * 100) if valid_pairs > 0 else 0
    avg_len_ratio = (sum(ratios) / len(ratios) * 100) if ratios else 0
    return {
        "success_rate": success_rate,
        "retention_acc": retention_acc,
        "avg_len_ratio": avg_len_ratio
    }
print("Loading original data...")
urls, originals = load_originals()
if not originals:
    print("No original emails loaded. Aborting.")
    exit()
summary_table = []
print(f"{'Model':<20} {'Task':<20} {'Retention':<15} {'Len Ratio':<15}")
print("-" * 70)
for model in MODELS:
    safe_model_name = model.replace(":", "_")
    model_dir = os.path.join(DATASETS_DIR, safe_model_name)
    if not os.path.exists(model_dir) and os.path.exists(os.path.join(DATASETS_DIR, model)):
            model_dir = os.path.join(DATASETS_DIR, model)
    shorten_path = os.path.join(model_dir, "shorten.jsonl")
    shorten_emails = load_generated(shorten_path)
    stats_std = calculate_metrics(urls, originals, shorten_emails)
    print(f"{model:<20} {'Shorten':<20} {stats_std['retention_acc']:6.2f}%       {stats_std['avg_len_ratio']:6.2f}%")
    summary_table.append({
        "Model": model,
        "Task": "Shorten",
        "Retention": stats_std['retention_acc'],
        "Ratio": stats_std['avg_len_ratio']
    })
    explicit_path = os.path.join(model_dir, "shorten_with_url.jsonl")
    explicit_emails = load_generated(explicit_path)
    stats_exp = calculate_metrics(urls, originals, explicit_emails)
    print(f"{model:<20} {'Shorten+URL':<20} {stats_exp['retention_acc']:6.2f}%       {stats_exp['avg_len_ratio']:6.2f}%")
    summary_table.append({
        "Model": model,
        "Task": "Shorten+URL",
        "Retention": stats_exp['retention_acc'],
        "Ratio": stats_exp['avg_len_ratio']
    })

if summary_table:
    tasks = ["Shorten", "Shorten+URL"]
    present_models = [m for m in MODELS if any(d["Model"] == m for d in summary_table)]
    if not present_models:
        present_models = sorted(list(set(d["Model"] for d in summary_table)))
    
    unique_models = present_models
    
    x = np.arange(len(unique_models))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, task in enumerate(tasks):
        values = []
        for model in unique_models:
            entry = next((item for item in summary_table if item["Model"] == model and item["Task"] == task), None)
            values.append(entry["Retention"] if entry else 0)
        
        pos = x + (i - 0.5) * width
        rects = ax.bar(pos, values, width, label=task)
        ax.bar_label(rects, padding=3, fmt='%.1f')

    ax.set_ylabel('Retention Accuracy (%)')
    ax.set_title('URL Retention by Model and Task')
    ax.set_xticks(x)
    ax.set_xticklabels(unique_models)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, task in enumerate(tasks):
        values = []
        for model in unique_models:
            entry = next((item for item in summary_table if item["Model"] == model and item["Task"] == task), None)
            values.append(entry["Ratio"] if entry else 0)
        
        pos = x + (i - 0.5) * width
        rects = ax.bar(pos, values, width, label=task)
        ax.bar_label(rects, padding=3, fmt='%.1f')

    ax.set_ylabel('Avg Length Ratio (%)')
    ax.set_title('Length Ratio by Model and Task')
    ax.set_xticks(x)
    ax.set_xticklabels(unique_models)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()
