import asyncio
from agents import Agent, Runner
from pathlib import Path
from dotenv import load_dotenv
from llm_clients.openai_client import OpenAIClient
from utils import load_env_variables, load_markdown_content
from llm_clients.claude_client import ClaudeClient
# from llm_clients.llama_client import LLaMAClient
# from llm_clients.deepseek_client import DeepSeekClient

async def create_agent_analyst(markdown_data: str) -> Agent:
    # client = OpenAIClient(model="gpt-4o")
    client = ClaudeClient(model="claude-3-5-sonnet-20241022")
    # client = LLaMAClient(model="llama3.2")
    # client = DeepSeekClient(model="deepseek-chat")

    return Agent(
        name="Booking Report Analyst",
        instructions=(
            f"""
            Você é um analista de dados especializado em consumo de espaços flexíveis e reservas empresariais.

            Ao receber:
            1. Uma pergunta em linguagem natural (já validada e dentro do escopo)
            2. Um documento em Markdown com os dados da empresa

            Sua missão é responder com clareza, objetividade e facilidade de leitura, gerando insights úteis com base somente nos dados fornecidos.

            Instruções:

            Apresente de 3 a 5 insights relevantes em tópicos (bullet points):
               - Seja direto e claro.
               - Destaque padrões, aumentos, quedas, ou qualquer dado que se destaque.
               - Evite jargões técnicos. Use linguagem acessível a gestores de qualquer área.

            3. Se não houver dados suficientes para responder à pergunta, escreva:
            Desculpe! Não encontramos dados suficientes para responder à sua pergunta neste momento.

            Importante:
            - Sempre baseie sua resposta apenas nos dados fornecidos no Markdown.
            - Nunca invente informações.
            - Mantenha o texto simples, visual e com foco em leitura rápida.

            - Em caso de agradecimento, responda de forma amigável e não forneça insights.

            Dados do relatório:
            {markdown_data}
            """
        ),
        model=client
    )

async def create_agent_judge(markdown_data: str) -> Agent:
    client = OpenAIClient(model="gpt-4o-mini")

    return Agent(
        name="Agent Judge",
        instructions=(
            f"""
                Você é um avaliador rigoroso.  Julgue a resposta do assistente com base **apenas** nos
                dados do Markdown fornecido.  Atribua notas de 0 a 10 para cada critério abaixo
                (exatidão, relevância, clareza_formato, insight).

                Retorne **somente** o JSON no formato:

                {{
                    "scores": {{
                        "exatidão": <0-10>,
                        "relevância": <0-10>,
                        "clareza_formato": <0-10>,
                        "insight": <0-10>
                    }},
                    "nota_geral": <0-100>,      # aplique os pesos definidos no código
                    "critica": "breve justificativa em português (1 parágrafo)"
                }}

                Regras adicionais:
                - Se a resposta inventar informações, defina exatidão = 0.
                - Se faltar qualquer critério, defina a nota desse critério = 0.
                - Nunca inclua explicações fora do JSON.

                Dados do relatório:
                {markdown_data}
            """
        ),
        model=client
    )

async def handle_question(agent: Agent, question: str):
    result = await Runner.run(agent, question)
    return result.final_output

def start_terminal_chat(agent: Agent, judge: Agent = None):
    print("💬 Chat inicializado com o Agente Facilities (digite 'exit' para sair)\n")

    async def chat_loop():
        while True:
            user_input = input("Usuário: ")
            if user_input.lower() in {"exit", "quit"}:
                print("👋 Saindo do chat.")
                break
            response = await handle_question(agent, user_input)
            print(f"Agente Facilities: {response}\n")
            if judge:
                prompt_judge = f"""
                    QUESTION:
                    {user_input}

                    ANSWER:
                    {response}
                """
                
                judge_response = await handle_question(judge, prompt_judge)
                print(f"Agente Judge: {judge_response}\n")

    asyncio.run(chat_loop())

def main():
    load_env_variables()
    markdown = load_markdown_content("./assets/relatorio-empresa-1810-fev-mar-abr.md")
    # markdown = load_markdown_content("./assets/relatorio-empresa-1010.md")
    agent = asyncio.run(create_agent_analyst(markdown))
    judge = asyncio.run(create_agent_judge(markdown))
    start_terminal_chat(agent, judge)


if __name__ == "__main__":
    main()