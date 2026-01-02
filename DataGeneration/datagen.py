import os
import yaml
import json
import random
import sys
import re
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generate import GenerateEmail
load_dotenv()
TOPICS = ['The benefits of remote work', 'How to improve team collaboration', 'The future of artificial intelligence in business']
PERSONAS = ['a marketing manager', 'a software engineer', 'a project manager']
TONES = ['professional', 'casual', 'enthusiastic']
LENGTHS = [50, 100, 150, 200]
TOTAL_REQUESTS = 100
generator = GenerateEmail(os.getenv('EVALUATOR_NAME'))
with open("output.jsonl", "a", encoding="utf-8") as f:
    for _ in range(TOTAL_REQUESTS):
        context = {
            "topic": random.choice(TOPICS),
            "persona": random.choice(PERSONAS),
            "length": random.choice(LENGTHS)
        }
        chosen_tone = random.choice(TONES)
        content = generator.generate(
            action='generate',
            selected_email=context,
            tone=chosen_tone
        )
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL)
        if match:
            content = match.group(1)
        result = {
            "topic": context["topic"],
            "persona": context["persona"],
            "tone": chosen_tone,
            "length": context["length"],
            "content": content
        }
        f.write(json.dumps(result, ensure_ascii=False) + "\n")
        f.flush()  
