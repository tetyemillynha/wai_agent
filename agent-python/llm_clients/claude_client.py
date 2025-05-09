from anthropic import AsyncAnthropic
from llm_clients.base import LLMClient

class ClaudeClient(LLMClient):
    def __init__(self, model: str = "claude-3-7-sonnet-20250219"):
        super().__init__(model)
        self.client = AsyncAnthropic()

    async def ask(self, prompt: str) -> str:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()