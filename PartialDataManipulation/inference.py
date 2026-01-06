import os
import json
import difflib
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

MODELS = [
    os.getenv("OLLAMA_MODEL"),
    os.getenv("OPENAI_MODEL_ONE"),
    os.getenv("OPENAI_MODEL_TWO")
]

MODELS = [m for m in MODELS if m]

DATASETS_DIR = "datasets"

def calculate_rouge_1(reference, hypothesis):
    """
    Computes ROUGE-1 Recall score (0 to 1).
    Recall = (Count of overlapping unigrams) / (Count of unigrams in reference)
    """
    if not reference:
        return 1.0 

    ref_tokens = reference.split()
    hyp_tokens = hypothesis.split()
    
    if len(ref_tokens) == 0:
        return 1.0 
        
    ref_counts = Counter(ref_tokens)
    hyp_counts = Counter(hyp_tokens)
    
    overlap = 0
    for token in ref_counts:
        overlap += min(ref_counts[token], hyp_counts[token])
        
    return overlap / len(ref_tokens)

def extract_generated_parts(full_generated, original_before, original_after):
    """
    Splits the generated text based on the lengths of the original before/after text.
    Assumes the model preserves the surrounding context length roughly or exactly.
    """
    if not full_generated:
        return "", "", ""

    len_before = len(original_before)
    len_after = len(original_after)
    len_gen = len(full_generated)

    if len_gen < len_before:
        gen_before = full_generated
        gen_selection = ""
        gen_after = ""
        return gen_before, gen_selection, gen_after

    gen_before = full_generated[:len_before]

    if len_after > 0:
        
        if len_gen - len_before < len_after:
             pass

        gen_after = full_generated[-len_after:]
        
        end_idx = len_gen - len_after
        if end_idx < len_before:
            end_idx = len_before
            
        gen_selection = full_generated[len_before : end_idx]
    else:
        gen_after = ""
        gen_selection = full_generated[len_before:]

    return gen_before, gen_selection, gen_after

def process_file(file_path):
    final_scores = []
    context_scores = []
    selection_scores = []
    
    if not os.path.exists(file_path):
        return [], [], []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line)
            except:
                continue
                
            original_before = record.get("text_before_selection", "")
            original_after = record.get("text_after_selection", "")
            original_selection = record.get("selection", "")
            full_generated = record.get("full_generated_email", "")
            
            if not original_before:
                gen_before = ""
                rem = full_generated
            else:
               gen_before, gen_mid, gen_aft = extract_generated_parts(full_generated, original_before, original_after)
            
            gen_before, gen_selection, gen_after = extract_generated_parts(full_generated, original_before, original_after)
            
            score_before = calculate_rouge_1(original_before, gen_before)
            
            score_after = calculate_rouge_1(original_after, gen_after)
            
            score_selection = calculate_rouge_1(original_selection, gen_selection)
            
            final_score = (score_before + score_after - score_selection) / 2.0
            
            context_score = (score_before + score_after) / 2.0
            
            selection_score = score_selection
            
            final_scores.append(final_score)
            context_scores.append(context_score)
            selection_scores.append(selection_score)
            
    return final_scores, context_scores, selection_scores

def print_ascii_table(headers, rows, title=None):
    if title:
        print(f"\n{title}")
    
    if not rows:
        print("No data to display.")
        return

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    separator = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    print(separator)
    header_row = "|" + "|".join(f" {h:<{w}} " for h, w in zip(headers, widths)) + "|"
    print(header_row)
    print(separator)

    for row in rows:
        data_row = "|" + "|".join(f" {str(c):<{w}} " for c, w in zip(row, widths)) + "|"
        print(data_row)
    
    print(separator)

def main():
    table_headers = ["Model", "Action", "Score"]
    
    final_rows = []
    context_rows = []
    selection_rows = []

    for model in MODELS:
        model_safe = model.replace(":", "_")
        model_dir = os.path.join(DATASETS_DIR, model_safe)
        
        if not os.path.isdir(model_dir):
            continue
            
        files = [f for f in os.listdir(model_dir) if f.endswith(".jsonl")]
        
        for file_name in files:
            file_path = os.path.join(model_dir, file_name)
            file_final, file_context, file_selection = process_file(file_path)
            
            avg_final = sum(file_final) / len(file_final) if file_final else 0.0
            avg_context = sum(file_context) / len(file_context) if file_context else 0.0
            avg_selection = sum(file_selection) / len(file_selection) if file_selection else 0.0
            
            final_rows.append([model_safe, file_name, f"{avg_final:.4f}"])
            context_rows.append([model_safe, file_name, f"{avg_context:.4f}"])
            selection_rows.append([model_safe, file_name, f"{avg_selection:.4f}"])
            
    print_ascii_table(table_headers, final_rows, title="Avg Final Score (Higher is Better)")
    print_ascii_table(table_headers, context_rows, title="Avg Context Score (Higher is Better)")
    print_ascii_table(table_headers, selection_rows, title="Avg Selection Score (High=No Change, Low=Change)")

if __name__ == "__main__":
    main()
