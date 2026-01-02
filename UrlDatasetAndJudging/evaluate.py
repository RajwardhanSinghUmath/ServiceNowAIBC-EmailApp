import json
import os
import pandas as pd # Optional, but good for tables. Use plain text formatting if pandas not guaranteed.
# I'll stick to plain text formatting to avoid dependencies if possible, or simple tabulation.

MODELS = ["gemma3:4b", "gpt-4.1", "gpt-4o-mini"]
DATASETS_DIR = "./datasets"

def load_originals():
    """Load the original emails and target URLs."""
    try:
        with open("random_good_urls.txt", "r") as f:
            target_urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        target_urls = []
        print("Warning: random_good_urls.txt not found.")

    original_emails = {}
    if os.path.exists("url_emails.jsonl"):
        with open("url_emails.jsonl", "r", encoding="utf-8") as f:
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
                        # Support both 'original_id' and 'id' if needed, but generate.py uses 'original_id'
                        oid = data.get('original_id')
                        # Content might be in 'Content', 'content', or body logic
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

    # Map ID to URL (assuming order matches ID 1..N)
    # verify logic: load_data in original script used enumerate(urls, 1) mapping to ID
    id_to_url = {i+1: url for i, url in enumerate(target_urls)}

    for eid, content in generated_emails.items():
        if eid not in original_emails:
            continue
        
        target_url = id_to_url.get(eid)
        if not target_url:
            continue

        # Check if URL in generated
        if target_url in content:
            url_found_count += 1
        
        # Check retention (if original had it)
        orig_content = original_emails[eid]
        if target_url in orig_content:
            valid_pairs += 1
            if target_url in content:
                retained_count += 1
        
        # Length ratio
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

def evaluate_all():
    print("Loading original data...")
    urls, originals = load_originals()
    
    if not originals:
        print("No original emails loaded. Aborting.")
        return

    summary_table = []

    print(f"{'Model':<20} {'Task':<20} {'Success Rate':<15} {'Retention':<15} {'Len Ratio':<15}")
    print("-" * 85)

    for model in MODELS:
        # Handle directory naming (sanitization)
        safe_model_name = model.replace(":", "_")
        model_dir = os.path.join(DATASETS_DIR, safe_model_name)
        
        # Fallback to unsanitized if sanitized doesn't exist
        if not os.path.exists(model_dir) and os.path.exists(os.path.join(DATASETS_DIR, model)):
             model_dir = os.path.join(DATASETS_DIR, model)

        # 1. Shorten (Standard)
        shorten_path = os.path.join(model_dir, "shorten.jsonl")
        shorten_emails = load_generated(shorten_path)
        stats_std = calculate_metrics(urls, originals, shorten_emails)
        
        print(f"{model:<20} {'Shorten':<20} {stats_std['success_rate']:6.2f}%       {stats_std['retention_acc']:6.2f}%       {stats_std['avg_len_ratio']:6.2f}%")
        
        summary_table.append({
            "Model": model,
            "Task": "Shorten",
            "Success": stats_std['success_rate'],
            "Retention": stats_std['retention_acc'],
            "Ratio": stats_std['avg_len_ratio']
        })

        # 2. Shorten with URL (Explicit)
        explicit_path = os.path.join(model_dir, "shorten_with_url.jsonl")
        explicit_emails = load_generated(explicit_path)
        stats_exp = calculate_metrics(urls, originals, explicit_emails)
        
        print(f"{model:<20} {'Shorten+URL':<20} {stats_exp['success_rate']:6.2f}%       {stats_exp['retention_acc']:6.2f}%       {stats_exp['avg_len_ratio']:6.2f}%")

        summary_table.append({
            "Model": model,
            "Task": "Shorten+URL",
            "Success": stats_exp['success_rate'],
            "Retention": stats_exp['retention_acc'],
            "Ratio": stats_exp['avg_len_ratio']
        })

if __name__ == "__main__":
    evaluate_all()