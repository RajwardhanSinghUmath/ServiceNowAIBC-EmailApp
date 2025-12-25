from openai import OpenAI
from dotenv import load_dotenv
import os
import yaml

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
        
        # TODO: implement this function to call ChatCompletions
        completion = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages
        )
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
    
    def generate(self, action: str,selected_email,tone="professional"):
        # TODO: implement your backend logic with this method. Skeleton code is provided below.
        if action == "shorten":
            # args = {"sender": "alice@solsticeanalytics.com", "subject": "Draft of Market Insights Report","content": "Hi team, I\u2019ve attached the newest draft of the Market Insights Report for your review. This version includes updated charts, competitor benchmarks, and revised projections through FY2026. Please take some time to look through the analysis\u2014especially the section on emerging trends in consumer behavior\u2014as I made several substantial edits based on our last meeting. If you notice any discrepancies, outdated references, or opportunities to clarify findings, feel free to leave comments directly in the doc. I\u2019d like to submit the final version to leadership by Thursday, so please aim to provide feedback by tomorrow afternoon. Thank you for your thoroughness as always."}
            args = selected_email
            system_prompt = self.get_prompt('shorten', prompt_type='system', **args)
            user_prompt = self.get_prompt('shorten', **args)
            return self.send_prompt(user_prompt, system_prompt)
        elif action == "lengthen":
            # args = {"sender": "alice@example.com", "subject": "Meeting Follow-Up", "content": "Hi, just checking in on the meeting notes."}
            args = selected_email
            system_prompt = self.get_prompt('lengthen', prompt_type='system', **args)
            user_prompt = self.get_prompt('lengthen', **args)
            return self.send_prompt(user_prompt, system_prompt)
        elif action == "tone":
            # tone=input("Enter the tone you want the mail to be in ?")
            # args = {"sender": "alice@example.com", "subject": "Meeting Follow-Up", "content": "Hi, just checking in on the meeting notes.","tone":tone}
            args = selected_email
            args["tone"]=tone
            system_prompt = self.get_prompt('tone', prompt_type='system', **args)
            user_prompt = self.get_prompt('tone', **args)
            return self.send_prompt(user_prompt, system_prompt)
        elif action == "faithfulness":
            args = selected_email
            system_prompt = self.get_prompt('faithfulness', prompt_type='system', **args)
            user_prompt = self.get_prompt('faithfulness', **args)
            return self.send_prompt(user_prompt, system_prompt)
        elif action == "completeness":
            args = selected_email
            system_prompt = self.get_prompt('completeness', prompt_type='system', **args)
            user_prompt = self.get_prompt('completeness', **args)
            return self.send_prompt(user_prompt, system_prompt)

generator = GenerateEmail(os.getenv('DEPLOYMENT_NAME'))
# print(generator.generate("shorten"))
# print(generator.generate("lengthen"))
# print(generator.generate("tone"))
