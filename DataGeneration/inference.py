import json
import matplotlib.pyplot as plt
import numpy as np
output={"topic": 0, "persona": 0, "tone": 0, "length": 0}
num_lines = sum(1 for line in open('./datasets/output_judge4.1-4o.jsonl', 'r', encoding='utf-8'))
with open('./datasets/output_judge4.1-4o.jsonl','r', encoding='utf-8') as f:
    for line in f:
        data_item=json.loads(line)
        output["topic"]+=int(data_item["evaluation"]["topic"])
        output["persona"]+=int(data_item["evaluation"]["persona"])
        output["tone"]+=int(data_item["evaluation"]["tone"])
        output["length"]+=int(data_item["evaluation"]["length"])
    output["topic"]/=num_lines
    output["persona"]/=num_lines
    output["tone"]/=num_lines
    output["length"]/=num_lines
output41=output
output={"topic": 0, "persona": 0, "tone": 0, "length": 0}
num_lines = sum(1 for line in open('./datasets/output_judge4o-4.1.jsonl', 'r', encoding='utf-8'))
with open('./datasets/output_judge4o-4.1.jsonl','r', encoding='utf-8') as f:
    for line in f:
        data_item=json.loads(line)
        output["topic"]+=int(data_item["evaluation"]["topic"])
        output["persona"]+=int(data_item["evaluation"]["persona"])
        output["tone"]+=int(data_item["evaluation"]["tone"])
        output["length"]+=int(data_item["evaluation"]["length"])
    output["topic"]/=num_lines
    output["persona"]/=num_lines
    output["tone"]/=num_lines
    output["length"]/=num_lines
output4o=output
output={"topic": 0, "persona": 0, "tone": 0, "length": 0}
num_lines = sum(1 for line in open('./datasets/output_judge_gemma4o.jsonl', 'r', encoding='utf-8'))
with open('./datasets/output_judge_gemma4o.jsonl','r', encoding='utf-8') as f:
    for line in f:
        data_item=json.loads(line)
        output["topic"]+=int(data_item["evaluation"]["topic"])
        output["persona"]+=int(data_item["evaluation"]["persona"])
        output["tone"]+=int(data_item["evaluation"]["tone"])
        output["length"]+=int(data_item["evaluation"]["length"])
    output["topic"]/=num_lines
    output["persona"]/=num_lines
    output["tone"]/=num_lines
    output["length"]/=num_lines
outputgemma4o=output
output={"topic": 0, "persona": 0, "tone": 0, "length": 0}
num_lines = sum(1 for line in open('./datasets/output_judge_gemma4.1.jsonl', 'r', encoding='utf-8'))
with open('./datasets/output_judge_gemma4.1.jsonl','r', encoding='utf-8') as f:
    for line in f:
        data_item=json.loads(line)
        output["topic"]+=int(data_item["evaluation"]["topic"])
        output["persona"]+=int(data_item["evaluation"]["persona"])
        output["tone"]+=int(data_item["evaluation"]["tone"])
        output["length"]+=int(data_item["evaluation"]["length"])
    output["topic"]/=num_lines
    output["persona"]/=num_lines
    output["tone"]/=num_lines
    output["length"]/=num_lines
outputgemma41=output
output={"topic": 0, "persona": 0, "tone": 0, "length": 0}
num_lines = sum(1 for line in open('./datasets/output_judge_4.1gemma.jsonl', 'r', encoding='utf-8'))
with open('./datasets/output_judge_4.1gemma.jsonl','r', encoding='utf-8') as f:
    for line in f:
        data_item=json.loads(line)
        output["topic"]+=int(data_item["evaluation"]["topic"])
        output["persona"]+=int(data_item["evaluation"]["persona"])
        output["tone"]+=int(data_item["evaluation"]["tone"])
        output["length"]+=int(data_item["evaluation"]["length"])
    output["topic"]/=num_lines
    output["persona"]/=num_lines
    output["tone"]/=num_lines
    output["length"]/=num_lines
output41gemma=output
output={"topic": 0, "persona": 0, "tone": 0, "length": 0}
num_lines = sum(1 for line in open('./datasets/output_judge_4.1gemma.jsonl', 'r', encoding='utf-8'))
with open('./datasets/output_judge_4.1gemma.jsonl','r', encoding='utf-8') as f:
    for line in f:
        data_item=json.loads(line)
        output["topic"]+=int(data_item["evaluation"]["topic"])
        output["persona"]+=int(data_item["evaluation"]["persona"])
        output["tone"]+=int(data_item["evaluation"]["tone"])
        output["length"]+=int(data_item["evaluation"]["length"])
    output["topic"]/=num_lines
    output["persona"]/=num_lines
    output["tone"]/=num_lines
    output["length"]/=num_lines
output4ogemma=output
print("GPT-4.1 Judged by GPT-4o-mini")
print(output41)
print("GPT-4o-mini Judged by GPT-4.1")
print(output4o)
print("GPT-4.1 Judged by Gemma")
print(outputgemma4o)
print("GPT-4o-mini Judged by Gemma")
print(outputgemma41)
print("Gemma Judged by GPT-4o-mini")
print(output41gemma)
print("Gemma Judged by GPT-4.1")
print(output4ogemma)
def count_words(s):
    l=s.split(" ")
    return len(l)
ratio_generated_by_asked=0
with open('./datasets/output4o.jsonl','r', encoding='utf-8') as f:
    for line in f:
        data_item=json.loads(line)
        generated=count_words(data_item["content"])
        asked=data_item["length"]
        ratio_generated_by_asked+=generated/asked
output4o_ratio = ratio_generated_by_asked
print("Length checked for output by gpt-4o-mini")
print(ratio_generated_by_asked)
ratio_generated_by_asked=0
with open('./datasets/output4.1.jsonl','r', encoding='utf-8') as f:
    for line in f:
        data_item=json.loads(line)
        generated=count_words(data_item["content"])
        asked=data_item["length"]
        ratio_generated_by_asked+=generated/asked
output41_ratio = ratio_generated_by_asked
print("Length checked for output by gpt-4.1")
print(ratio_generated_by_asked)
ratio_generated_by_asked=0
with open('./datasets/output_gemma.jsonl','r', encoding='utf-8') as f:
    for line in f:
        data_item=json.loads(line)
        generated=count_words(data_item["content"])
        asked=data_item["length"]
        ratio_generated_by_asked+=generated/asked
print("Length checked for output by gemma-3-4b")
print(ratio_generated_by_asked)
gemma_ratio = ratio_generated_by_asked

scenarios = [
    ("GPT-4.1 (by 4o-mini)", output41),
    ("GPT-4o-mini (by 4.1)", output4o),
    ("GPT-4.1 (by Gemma)", outputgemma4o),
    ("GPT-4o-mini (by Gemma)", outputgemma41),
    ("Gemma (by 4o-mini)", output41gemma),
    ("Gemma (by 4.1)", output4ogemma)
]

labels = [s[0] for s in scenarios]
topics = [s[1]["topic"] for s in scenarios]
personas = [s[1]["persona"] for s in scenarios]
tones = [s[1]["tone"] for s in scenarios]
lengths_scores = [s[1]["length"] for s in scenarios]

x = np.arange(len(labels))
width = 0.2

fig, ax = plt.subplots(figsize=(14, 7))
rects1 = ax.bar(x - 1.5*width, topics, width, label='Topic')
rects2 = ax.bar(x - 0.5*width, personas, width, label='Persona')
rects3 = ax.bar(x + 0.5*width, tones, width, label='Tone')
rects4 = ax.bar(x + 1.5*width, lengths_scores, width, label='Length Score')

ax.set_ylabel('Scores')
ax.set_title('Evaluation Metrics by Scenario')
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha='right')
ax.legend()

ax.bar_label(rects1, padding=3, fmt='%.1f')
ax.bar_label(rects2, padding=3, fmt='%.1f')
ax.bar_label(rects3, padding=3, fmt='%.1f')
ax.bar_label(rects4, padding=3, fmt='%.1f')

fig.tight_layout()
plt.show()
models_ratios = ["GPT-4o-mini", "GPT-4.1", "Gemma-3-4b"]
ratios = [output4o_ratio, output41_ratio, gemma_ratio]

plt.figure(figsize=(8, 6))
bars = plt.bar(models_ratios, ratios, color=['#1f77b4', '#ff7f0e', '#2ca02c'])

plt.xlabel('Model')
plt.ylabel('Avg Length Ratio (Generated/Asked)')
plt.title('Average Length Ratio Compliance')
plt.bar_label(bars, fmt='%.2f')

plt.tight_layout()
plt.show()
