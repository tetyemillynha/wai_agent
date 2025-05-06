import asyncio
from agents import Agent, Runner
from pathlib import Path
from dotenv import load_dotenv
import os

def load_env_variables():
    load_dotenv()

def load_markdown_content(filepath: str) -> str:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    return path.read_text(encoding="utf-8")

def create_agent(markdown_data: str) -> Agent:
    return Agent(
        name="Booking Report Analyst",
        instructions=(
            "Você é um analista de dados especializado em consumo de espaços flexíveis e reservas empresariais.\n\n"
            "Ao receber:\n"
            "1. Uma pergunta em linguagem natural (já validada e dentro do escopo)\n"
            "2. Um documento em Markdown com os dados da empresa\n\n"
            "Sua missão é responder com clareza, objetividade e facilidade de leitura, gerando insights úteis com base somente nos dados fornecidos.\n\n"
            "Instruções:\n\n"
            "1. Comece com o título:\n"
            "🔍 O que encontramos para você\n\n"
            "2. Em seguida, apresente de 3 a 5 insights relevantes em tópicos (bullet points):\n"
            "   - Seja direto e claro.\n"
            "   - Destaque padrões, aumentos, quedas, ou qualquer dado que se destaque.\n"
            "   - Evite jargões técnicos. Use linguagem acessível a gestores de qualquer área.\n\n"
            "3. Se não houver dados suficientes para responder à pergunta, escreva:\n"
            "Desculpe! Não encontramos dados suficientes para responder à sua pergunta neste momento.\n\n"
            "Exemplo de resposta:\n\n"
            "---\n\n"
            "O que encontramos para você\n\n"
            "- A empresa consumiu 2.130 créditos no período analisado.\n"
            "- O espaço mais utilizado foi a Sala Reunião A, com 56% do total.\n"
            "- O grupo \"Comercial\" foi responsável por 40% das reservas.\n"
            "- Houve uma queda de 18% no consumo em março comparado a fevereiro.\n\n"
            "---\n\n"
            "Importante:\n"
            "- Sempre baseie sua resposta apenas nos dados fornecidos no Markdown.\n"
            "- Nunca invente informações.\n"
            "- Mantenha o texto simples, visual e com foco em leitura rápida.\n\n"
            "Dados do relatório:\n"
            f"{markdown_data}"
        ),
        model="gpt-4o"
    )

async def handle_question(agent: Agent, question: str):
    result = await Runner.run(agent, question)
    return result.final_output

def start_terminal_chat(agent: Agent):
    print("💬 Chat inicializado com o Agente Facilities (digite 'exit' para sair)\n")

    async def chat_loop():
        while True:
            user_input = input("Usuário: ")
            if user_input.lower() in {"exit", "quit"}:
                print("👋 Saindo do chat.")
                break
            response = await handle_question(agent, user_input)
            print(f"Agente Facilities: {response}\n")

    asyncio.run(chat_loop())

def main():
    load_env_variables()
    markdown = load_markdown_content("./assets/relatorio-empresa-1810.md")
    agent = create_agent(markdown)
    start_terminal_chat(agent)

if __name__ == "__main__":
    main()