from dataclasses import dataclass
from llm_clients.base import LLMClient

@dataclass
class Agent:
    name: str
    instructions: str
    model: LLMClient