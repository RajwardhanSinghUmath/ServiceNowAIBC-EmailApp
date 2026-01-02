import json
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
print("Length checked for output by gpt-4o-mini")
print(ratio_generated_by_asked)
ratio_generated_by_asked=0
with open('./datasets/output4.1.jsonl','r', encoding='utf-8') as f:
    for line in f:
        data_item=json.loads(line)
        generated=count_words(data_item["content"])
        asked=data_item["length"]
        ratio_generated_by_asked+=generated/asked
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
