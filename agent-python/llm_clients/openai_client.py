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

    async def summarize(self, markdown: str) -> str:
        prompt = (
            "Você receberá a seguir um relatório em formato Markdown com dados detalhados sobre reservas de uma empresa, "
            "incluindo informações de consumo de créditos, grupos de usuários, espaços utilizados, e status das reservas.\n\n"
            "Sua tarefa é resumir esse relatório **mantendo os dados brutos mais relevantes**, de forma que o resumo contenha:\n"
            "- Total de créditos consumidos\n"
            "- Lista dos grupos que mais consumiram créditos (com valores)\n"
            "- Espaços mais utilizados (com quantidades ou percentuais)\n"
            "- Datas ou períodos com maior concentração de uso\n"
            "- Qualquer padrão de cancelamentos ou quedas no uso\n\n"
            "**Importante:**\n"
            "- NÃO gere conclusões ou interpretações.\n"
            "- NÃO invente dados.\n"
            "- Apenas resuma os dados reais apresentados, priorizando aqueles com maior impacto ou volume.\n"
            "- O texto deve ser objetivo, no mesmo formato Markdown se possível (listas, seções, subtítulos).\n\n"
            "A seguir está o conteúdo do relatório original:\n\n"
            f"{markdown[:20000]}"
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Você é um assistente de análise de dados de consumo de créditos para reservas de espaços flexíveis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2048
        )

        return response.choices[0].message.content.strip()