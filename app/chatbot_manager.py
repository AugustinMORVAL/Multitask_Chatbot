from groq import Groq

class ChatbotManager:
    def __init__(self, api_key, models):
        self.client = Groq(api_key=api_key)
        self.models = models

    def get_response(self, model, messages, temperature, max_tokens, **kwargs):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content