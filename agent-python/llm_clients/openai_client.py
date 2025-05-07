from openai import AsyncOpenAI
from llm_clients.base import LLMClient

class OpenAIClient(LLMClient):
    def __init__(self, model: str):
        super().__init__(model)
        self.client = AsyncOpenAI()

    async def ask(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        return response.choices[0].message.content.strip()