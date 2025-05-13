import uuid
import csv
import os
from datetime import datetime
from openai import AsyncOpenAI
from httpx import AsyncClient, Timeout
from llm_clients.base import LLMClient

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "openai_tracing_logs.csv")
os.makedirs(LOG_DIR, exist_ok=True)

def log_to_csv(trace_id, request_id, response, model, judging_model: str = ""):
    file_path = f"logs/{judging_model}_logs.csv"
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["timestamp", "trace_id", "request_id", "model", "judging_model", "response"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": trace_id,
            "request_id": request_id,
            "model": model,
            "judging_model": judging_model,
            "response": response,
        })

class OpenAIClient(LLMClient):
    def __init__(self, model: str, judging_model: str = ""):
        super().__init__(model)
        self.judging_model = judging_model
        timeout = Timeout(30.0) 
        self.http_client = AsyncClient(timeout=timeout)
        self.client = AsyncOpenAI(http_client=self.http_client)

    async def ask(self, prompt: str) -> str:
        trace_id = str(uuid.uuid4())

        response = await self.http_client.post(
            url="https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.client.api_key}",
                "Content-Type": "application/json",
                "OpenAI-Client-Trace-Id": trace_id
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}]
            }
        )

        response_json = response.json()
        request_id = response.headers.get("x-request-id", "unknown")
        reply = response_json["choices"][0]["message"]["content"].strip()

        log_to_csv(trace_id, request_id, reply, self.model, self.judging_model)

        return reply