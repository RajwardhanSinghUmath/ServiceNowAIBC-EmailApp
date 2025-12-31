import json
output={"topic": 0, "persona": 0, "tone": 0, "length": 0}

num_lines = sum(1 for line in open('output_judge4.1-4o.jsonl', 'r', encoding='utf-8'))

with open('output_judge4.1-4o.jsonl','r', encoding='utf-8') as f:
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

num_lines = sum(1 for line in open('output_judge4o-4.1.jsonl', 'r', encoding='utf-8'))
with open('output_judge4o-4.1.jsonl','r', encoding='utf-8') as f:
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

print(output41)
print(output4o)

# {'topic': 5.0, 'persona': 4.86, 'tone': 4.94, 'length': 4.36}
# {'topic': 5.0, 'persona': 4.98, 'tone': 4.96, 'length': 3.83}
# GPT-4o-mini is less adhering to length there might be a bias of models involved in the other metrics though
 
def count_words(s):
    l=s.split(" ")
    return len(l)

ratio_generated_by_asked=0
with open('output4o.jsonl','r', encoding='utf-8') as f:
    for line in f:
        data_item=json.loads(line)
        generated=count_words(data_item["content"])
        asked=data_item["length"]
        ratio_generated_by_asked+=generated/asked
print(ratio_generated_by_asked)

ratio_generated_by_asked=0
with open('output4.1.jsonl','r', encoding='utf-8') as f:
    for line in f:
        data_item=json.loads(line)
        generated=count_words(data_item["content"])
        asked=data_item["length"]
        ratio_generated_by_asked+=generated/asked
print(ratio_generated_by_asked)

# 99.19333333333336
# 97.84499999999996
# still the score is too low for this, LLMs preferring longer responses might be a reason
