from groq import Groq
import re

class ChatbotManager:
    def __init__(self, api_key, config):
        self.client = Groq(api_key=api_key)
        self.models = config['models']
        self.config = config

    def get_response(self, model, messages, temperature, max_tokens, cot_reflection=False, show_process=False, **kwargs):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        full_response = response.choices[0].message.content

        if not cot_reflection:
            return full_response
        else:
            return self._cot_reflection(full_response, show_process)
        
    def _cot_reflection(self, full_response, show_process: bool=False):
        tags = self.config['cot_reflection']['tags']

        if show_process:
            formatted_response = ""
            for tag, icon in tags.items():
                pattern = f'<{tag}>(.*?)</{tag}>'
                match = re.search(pattern, full_response, re.DOTALL)
                if match:
                    content = match.group(1).strip()
                    formatted_response += f"{icon} **{tag.capitalize()}:**\n{content}\n\n"
            return formatted_response.strip()
        else:
            output_match = re.search(r'<output>(.*?)</output>', full_response, re.DOTALL)
            return output_match.group(1).strip() if output_match else full_response

