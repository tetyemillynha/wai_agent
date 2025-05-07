import httpx
from llm_clients.base import LLMClient

class LLaMAClient(LLMClient):
    def __init__(self, model: str = "llama3.2"):
        super().__init__(model)
        self.endpoint = "http://localhost:11434/api/generate"

    async def ask(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(self.endpoint, json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                })
                response.raise_for_status()
                return response.json().get("response", "").strip()
            except httpx.HTTPError as e:
                return f"Erro ao chamar o modelo LLaMA: {str(e)}"