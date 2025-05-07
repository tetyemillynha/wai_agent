# llm_clients/base.py
class LLMClient:
    def __init__(self, model: str):
        self.model = model

    async def ask(self, prompt: str) -> str:
        raise NotImplementedError("ask method must be implemented")
