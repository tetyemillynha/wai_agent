import uuid
import os
import csv
from datetime import datetime
import httpx
from llm_clients.base import LLMClient

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "claude_tracing_logs.csv")
os.makedirs(LOG_DIR, exist_ok=True)

def log_to_csv(trace_id, request_id, response, response_model, judging_model):
    file_path = f"logs/{judging_model}_logs.csv"
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode='a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["timestamp", "trace_id", "request_id", "response_model", "judging_model", "response"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": trace_id,
            "request_id": request_id,
            "response_model": response_model,
            "judging_model": judging_model,
            "response": response
        })

class ClaudeClient(LLMClient):
    def __init__(self, model: str = "claude-3-7-sonnet-20250219", judging_model: str = ""):
        super().__init__(model)
        self.client = httpx.AsyncClient(timeout=30.0)
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.judging_model = judging_model or model 

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY não está definida.")

    async def ask(self, prompt: str) -> str:
        trace_id = str(uuid.uuid4())

        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        headers = {
            "x-api-key": self.api_key, 
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            "X-Trace-Id": trace_id
        }

        response = await self.client.post(
            "https://api.anthropic.com/v1/messages",
            json=payload,
            headers=headers
        )

        response.raise_for_status()

        json_data = response.json()
        reply = json_data["content"][0]["text"].strip()
        request_id = response.headers.get("anthropic-request-id", "unknown")

        log_to_csv(trace_id, request_id, reply, self.model, self.judging_model)

        return reply
