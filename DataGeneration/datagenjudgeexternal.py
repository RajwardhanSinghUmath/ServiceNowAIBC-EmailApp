import os
import yaml
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

with open("../prompts.yaml", "r") as f:
    prompts = yaml.safe_load(f)

class OllamaJudge():    
    def __init__(self, model: str):
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )
        self.deployment_name = model

    def _call_api(self, messages):
        try:
            completion = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                response_format={"type": "json_object"}
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return "{}"
    
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

judger = OllamaJudge("gemma3:4b")

input_file = "output4o.jsonl"
output_file = "output_judge_gemma4o.jsonl"

if os.path.exists(input_file):
    with open(input_file, "r", encoding="utf-8") as f_in, \
         open(output_file, "w", encoding="utf-8") as f_out: 
        
        for line in f_in:
            if not line.strip():
                continue
                
            data_item = json.loads(line)
            
            if "content" in data_item:
                print(f"Judging email regarding {data_item.get('topic', 'unknown')}...")
                result = judger.judge(
                    topic=data_item.get("topic", "N/A"),
                    persona=data_item.get("persona", "N/A"),
                    tone=data_item.get("tone", "N/A"),
                    length=data_item.get("length", "N/A"),
                    content=data_item.get("content", "")
                )
                
                f_out.write(json.dumps(result, ensure_ascii=False) + "\n")
                f_out.flush()
    print(f"Done. Results saved to {output_file}")
else:
    print(f"Input file {input_file} not found.")
