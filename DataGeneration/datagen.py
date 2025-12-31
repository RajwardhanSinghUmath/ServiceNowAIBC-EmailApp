import os
import yaml
import json
import random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
with open("../prompts.yaml", "r") as f:
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
            messages=messages
        )
        return completion.choices[0].message.content
    
    def get_prompt(self, prompt_name, prompt_type='user', **kwargs):
        template = prompts[prompt_name][prompt_type]
        return template.format(**kwargs)
    
    def generate(self, topic, persona, tone, length):
        system_prompt = self.get_prompt('generate', 'system', topic=topic, persona=persona, tone=tone, length=length)
        user_prompt = self.get_prompt('generate', topic=topic, persona=persona, tone=tone, length=length)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        content = self._call_api(messages)

        return {
            "topic": topic,
            "persona": persona,
            "tone": tone,
            "length": length,
            "content": content
        }

TOPICS = ['The benefits of remote work', 'How to improve team collaboration', 'The future of artificial intelligence in business']
PERSONAS = ['a marketing manager', 'a software engineer', 'a project manager']
TONES = ['professional', 'casual', 'enthusiastic']
LENGTHS = [50, 100, 150, 200]
TOTAL_REQUESTS = 100

generator = GenerateEmail(os.getenv('EVALUATOR_NAME'))

with open("output.jsonl", "a", encoding="utf-8") as f:
    for _ in range(TOTAL_REQUESTS):
        result = generator.generate(
            topic=random.choice(TOPICS),
            persona=random.choice(PERSONAS),
            tone=random.choice(TONES),
            length=random.choice(LENGTHS)
        )
        
        f.write(json.dumps(result, ensure_ascii=False) + "\n")
        f.flush()  