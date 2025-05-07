import os
import httpx
from llm_clients.base import LLMClient

class DeepSeekClient(LLMClient):
    def __init__(self, model: str = "deepseek-chat"):
        super().__init__(model)
        self.endpoint = "https://api.deepseek.com/v1/chat/completions"
        self.api_key = os.getenv("DEEPSEEK_API_KEY")

        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY não está definido no .env")

    async def ask(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Você é um analista de dados especializado em consumo de espaços flexíveis. Responda com base nos dados fornecidos em markdown."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1024,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(self.endpoint, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"].strip()
            except httpx.HTTPStatusError as e:
                return f"Erro ao chamar a API da DeepSeek: {e.response.status_code} - {e.response.text}"
            except httpx.HTTPError as e:
                return f"Erro ao chamar a API da DeepSeek: {str(e)}"