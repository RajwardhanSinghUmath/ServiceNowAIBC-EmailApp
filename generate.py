from openai import OpenAI
from dotenv import load_dotenv
import os
import yaml
import json
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_PATH = os.path.join(BASE_DIR, "prompts.yaml")
with open(PROMPTS_PATH, "r") as f:
    prompts = yaml.safe_load(f)
class GenerateEmail():    
    def __init__(self, model: str):
        self.deployment_name = model
        cleaned_model = model.lower() if model else ""
        if "gemma" in cleaned_model:
            self.client = OpenAI(
                base_url=os.getenv("OLLAMA_API_BASE"),
                api_key=os.getenv("OLLAMA_API_KEY"),
            )
        else:
            self.client = OpenAI(
                base_url=os.getenv("OPENAI_API_BASE"),
                api_key=os.getenv("OPENAI_API_KEY"),
            )
    def _call_api(self, messages):
        kwargs = {
            "model": self.deployment_name,
            "messages": messages
        }
        completion = self.client.chat.completions.create(**kwargs)
        return completion.choices[0].message.content
    def get_prompt(self, prompt_name, prompt_type='user', **kwargs):
        template = prompts[prompt_name][prompt_type]
        return template.format(**kwargs)
    def send_prompt(self, user_prompt: str, system_msg="You are a helpful assistant."):
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt}
        ]
        return self._call_api(messages)
    def generate(self, action: str, selected_email, tone=None, **kwargs):
        args = selected_email.copy() if isinstance(selected_email, dict) else {}
        if tone:
            args["tone"] = tone
        args.update(kwargs) 
        system_prompt = self.get_prompt(action, prompt_type='system', **args)
        user_prompt = self.get_prompt(action, **args)
        return self.send_prompt(user_prompt, system_prompt)
if __name__ == "__main__":
    generator = GenerateEmail(os.getenv('DEPLOYMENT_NAME'))
