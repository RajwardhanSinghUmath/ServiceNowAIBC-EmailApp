import json
import os

def load_data():
    with open("random_good_urls.txt", "r") as f:
        target_urls = [line.strip() for line in f if line.strip()]
    
    original_emails = {}
    if os.path.exists("url_emails.jsonl"):
        with open("url_emails.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    original_emails[data['id']] = data.get('content', '')
    
    shortened_emails = {}
    if os.path.exists("shortened_url_emails.jsonl"):
        with open("shortened_url_emails.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    oid = data.get('original_id')
                    if oid:
                        shortened_emails[oid] = data.get('Content', '')

    explicit_shortened_emails = {}
    if os.path.exists("shortened_explicit_url_emails.jsonl"):
        with open("shortened_explicit_url_emails.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    oid = data.get('original_id')
                    if oid:
                        explicit_shortened_emails[oid] = data.get('Content', '')
    
    return target_urls, original_emails, shortened_emails, explicit_shortened_emails

def evaluate():
    print("Loading data...")
    urls, originals, shortens, explicit_shortens = load_data()
    
    total_urls = len(urls)
    total_originals = len(originals)
    total_shortens = len(shortens)
    total_explicit = len(explicit_shortens)
    
    print(f"Loaded {total_urls} Target URLs")
    print(f"Loaded {total_originals} Original Emails")
    print(f"Loaded {total_shortens} Shortened Emails (Standard)")
    print(f"Loaded {total_explicit} Shortened Emails (Explicit)")
    
    if total_originals == 0:
        print("No original emails found. Exiting.")
        return

    url_found_in_original = 0
    url_found_in_shortened = 0
    url_found_in_explicit = 0
    
    results = []
    
    for i, target_url in enumerate(urls, 1):
        email_id = i
        
        original_has_url = False
        if email_id in originals:
            if target_url in originals[email_id]:
                original_has_url = True
                url_found_in_original += 1
        
        shortened_has_url = False
        if email_id in shortens:
            if target_url in shortens[email_id]:
                shortened_has_url = True
                url_found_in_shortened += 1

        explicit_has_url = False
        if email_id in explicit_shortens:
            if target_url in explicit_shortens[email_id]:
                explicit_has_url = True
                url_found_in_explicit += 1
        
        results.append({
            "id": email_id,
            "url": target_url,
            "in_original": original_has_url,
            "in_shortened": shortened_has_url,
            "in_explicit": explicit_has_url
        })

    original_success_rate = (url_found_in_original / total_originals * 100) if total_originals > 0 else 0
    shorten_success_rate = (url_found_in_shortened / total_shortens * 100) if total_shortens > 0 else 0
    explicit_success_rate = (url_found_in_explicit / total_explicit * 100) if total_explicit > 0 else 0
    
    valid_pairs_std = 0
    retained_in_std = 0
    
    for res in results:
        eid = res['id']
        if eid in originals and eid in shortens:
            if res['in_original']:
                valid_pairs_std += 1
                if res['in_shortened']:
                    retained_in_std += 1

    retention_accuracy_std = (retained_in_std / valid_pairs_std * 100) if valid_pairs_std > 0 else 0

    valid_pairs_exp = 0
    retained_in_exp = 0
    
    for res in results:
        eid = res['id']
        if eid in originals and eid in explicit_shortens:
            if res['in_original']:
                valid_pairs_exp += 1
                if res['in_explicit']:
                    retained_in_exp += 1

    retention_accuracy_exp = (retained_in_exp / valid_pairs_exp * 100) if valid_pairs_exp > 0 else 0

    
    ratios_std = []
    for eid, orig_content in originals.items():
        if eid in shortens:
            orig_words = len(orig_content.split())
            short_words = len(shortens[eid].split())
            if orig_words > 0:
                ratios_std.append(short_words / orig_words)

    ratios_exp = []
    for eid, orig_content in originals.items():
        if eid in explicit_shortens:
            orig_words = len(orig_content.split())
            short_words = len(explicit_shortens[eid].split())
            if orig_words > 0:
                ratios_exp.append(short_words / orig_words)

    avg_ratio_std = (sum(ratios_std) / len(ratios_std) * 100) if ratios_std else 0
    avg_ratio_exp = (sum(ratios_exp) / len(ratios_exp) * 100) if ratios_exp else 0

    print("\n" + "="*40)
    print("       EVALUATION REPORT       ")
    print("="*40)
    print(f"Original Emails Checked: {total_originals}")
    print(f"  - contain URL: {url_found_in_original}")
    print(f"  - Success Rate: {original_success_rate:.2f}%")
    
    print("-" * 40)
    print(f"Shortened Emails (Standard) Checked: {total_shortens}")
    print(f"  - contain URL: {url_found_in_shortened}")
    print(f"  - Success Rate: {shorten_success_rate:.2f}%")
    if valid_pairs_std > 0:
        print(f"  - Retention Accuracy (where original had URL): {retention_accuracy_std:.2f}% ({retained_in_std}/{valid_pairs_std})")
    print(f"  - Average Length Ratio: {avg_ratio_std:.2f}% of original size")
    
    print("-" * 40)
    print(f"Shortened Emails (Explicit) Checked: {total_explicit}")
    print(f"  - contain URL: {url_found_in_explicit}")
    print(f"  - Success Rate: {explicit_success_rate:.2f}%")
    if valid_pairs_exp > 0:
        print(f"  - Retention Accuracy (where original had URL): {retention_accuracy_exp:.2f}% ({retained_in_exp}/{valid_pairs_exp})")
    print(f"  - Average Length Ratio: {avg_ratio_exp:.2f}% of original size")
    
    print("="*40)

if __name__ == "__main__":
    evaluate()

# ========================================
#        EVALUATION REPORT
# ========================================
# Original Emails Checked: 100
#   - contain URL: 100
#   - Success Rate: 100.00%
# ----------------------------------------
# Shortened Emails (Standard) Checked: 100
#   - contain URL: 73
#   - Success Rate: 73.00%
#   - Retention Accuracy (where original had URL): 73.00% (73/100)  
#   - Average Length Ratio: 22.54% of original size
# ----------------------------------------
# Shortened Emails (Explicit) Checked: 100
#   - contain URL: 100
#   - Success Rate: 100.00%
#   - Retention Accuracy (where original had URL): 100.00% (100/100)
#   - Average Length Ratio: 23.03% of original size
# ========================================