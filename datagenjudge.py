import os
import yaml
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
with open("prompts.yaml", "r") as f:
    prompts = yaml.safe_load(f)

class GenerateEmail():    
    def __init__(self, model: str):
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_API_BASE"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.deployment_name = model

    def _call_api(self, messages):
        completion = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages,
            response_format={"type": "json_object"}
        )
        return completion.choices[0].message.content
    
    def get_prompt(self, prompt_name, prompt_type='user', **kwargs):
        template = prompts[prompt_name][prompt_type]
        return template.format(**kwargs)
    
    def judge(self, topic, persona, tone, length, content):
        system_prompt = self.get_prompt('judge_generation', 'system', 
                                       topic=topic, persona=persona, tone=tone, 
                                       length=length, content=content)
        user_prompt = self.get_prompt('judge_generation', 
                                     topic=topic, persona=persona, tone=tone, 
                                     length=length, content=content)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        raw_judge_output = self._call_api(messages)
        
        try:
            score_data = json.loads(raw_judge_output)
        except:
            score_data = {"error": "failed_to_parse", "raw": raw_judge_output}

        return {
            "topic": topic,
            "persona": persona,
            "evaluation": score_data
        }

judger = GenerateEmail(os.getenv('DEPLOYMENT_NAME'))

input_file = "output.jsonl"
output_file = "output_judge1.jsonl"

num_lines = sum(1 for line in open(input_file, 'r', encoding='utf-8'))

with open(input_file, "r", encoding="utf-8") as f_in, \
     open(output_file, "a", encoding="utf-8") as f_out:
    
    for line in f_in:
        if not line.strip():
            continue
            
        data_item = json.loads(line)
        
        result = judger.judge(**data_item)
        
        f_out.write(json.dumps(result, ensure_ascii=False) + "\n")
        f_out.flush()
