import asyncio
from agents import Agent, Runner, ModelSettings
from utils import load_env_variables, load_json_content

gpt_instructions = """
Você é um analista de dados experiente. Responda com precisão e evite inferências que não estejam diretamente sustentadas pelos dados.

Você receberá:
1. Uma pergunta em linguagem natural, já validada e dentro do escopo
2. Um documento em JSON (markdown estruturado) com os dados da empresa

Sua missão é:
- Gerar uma resposta clara, objetiva e fácil de ler
- Apresentar insights úteis e relevantes com base **exclusiva** nos dados fornecidos

### Instruções para sua resposta:
- Responda em tópicos (bullet points), com **de 3 a 6 insights**
- Estruture os insights com subtítulos claros, ex: "**Top Grupos com Risco**", "**Cidades com Maior Gasto por Reserva**", etc.
- Use linguagem simples, acessível a gestores, evitando jargões técnicos
- Destaque padrões, aumentos, quedas, desvios ou comparativos relevantes
- Não invente informações. **Baseie-se estritamente nos dados**
- Se houver limitação de dados, mencione de forma sutil e profissional (sem pedir mais informações)

### Importante:
- Nunca faça suposições ou projeções que não estejam nos dados
- Não solicite dados adicionais ao usuário
- Caso a pergunta seja apenas um agradecimento, responda de forma amigável, sem gerar insights
"""

sonnet_3_5_instructions = """
Você é um analista de dados especializado em consumo de espaços flexíveis e reservas empresariais.

Ao receber:
   1. Uma pergunta em linguagem natural (já validada e dentro do escopo)
   2. Um documento em JSON com os dados da empresa

Sua missão é responder com clareza, objetividade e facilidade de leitura, gerando insights úteis com base somente nos dados fornecidos.

Instruções:

Apresente de 3 a 5 insights relevantes em tópicos (bullet points):
      - Seja direto e claro.
      - Destaque padrões, aumentos, quedas, ou qualquer dado que se destaque.
      - Evite jargões técnicos. Use linguagem acessível a gestores de qualquer área.
      - Indicar limitações de forma sutil e sem solicitar mais dados ao usuário.

   3. Se não houver dados suficientes para responder à pergunta, não solicite mais informações ao usuário e escreva:
   Desculpe! Não encontramos dados suficientes para responder à sua pergunta neste momento.

   
Importante:
   - Sempre baseie sua resposta apenas nos dados fornecidos no JSON.
   - Nunca invente informações.
   - Mantenha o texto simples, visual e com foco em leitura rápida.

   - Em caso de agradecimento, responda de forma amigável e não forneça insights.
"""

sonnet_3_7_instructions = """
Você é um analista de dados sênior. Sua tarefa é gerar uma resposta objetiva, útil e visualmente organizada com base **somente nos dados fornecidos**.

Ao receber:
   1. Uma pergunta em linguagem natural (já validada e dentro do escopo)
   2. Um documento em JSON com os dados da empresa

Sua missão é responder com clareza, objetividade e facilidade de leitura, gerando insights úteis com base somente nos dados fornecidos.

Instruções:

Apresente de 3 a 5 insights relevantes em tópicos (bullet points):
      - Seja direto e claro.
      - Destaque padrões, aumentos, quedas, ou qualquer dado que se destaque.
      - Evite jargões técnicos. Use linguagem acessível a gestores de qualquer área.
      - Indicar limitações de forma sutil e sem solicitar mais dados ao usuário.

   3. Se não houver dados suficientes para responder à pergunta, não solicite mais informações ao usuário e escreva:
   Desculpe! Não encontramos dados suficientes para responder à sua pergunta neste momento.

   
Importante:
   - Sempre baseie sua resposta apenas nos dados fornecidos no JSON.
   - Nunca invente informações.
   - Mantenha o texto simples, visual e com foco em leitura rápida.

   - Em caso de agradecimento, responda de forma amigável e não forneça insights.

"""

async def create_agent_analyst(markdown_data: str) -> Agent:
    # model = "litellm/anthropic/claude-3-5-sonnet-20240620"
    # model = "litellm/anthropic/claude-3-7-sonnet-20250219"
    model = "gpt-4o"

    # 3.5 não ficou legal ajustando os parâmetros
    model_settings_sonnet_3_5 = ModelSettings(
        temperature=0.1,
        top_p=1,
        max_tokens=2500
    )

    model_settings_sonnet_3_7 = ModelSettings(
        temperature=0.0,
        top_p=1,
        max_tokens=2500
    )

    model_settings_gpt_4o = ModelSettings(
        temperature=0.1,
        top_p=1,
        max_tokens=3000,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    return Agent(
        name="Booking Report Analyst",
        instructions=(
            f"""
            {gpt_instructions}

            Dados do relatório:
            {markdown_data}
            """
        ),
        model=model,
        model_settings=model_settings_gpt_4o
    )

async def create_agent_judge(markdown_data: str) -> Agent:
    return Agent(
        name="Agent Judge",
        instructions=(
            f"""
                Você é um avaliador rigoroso.  Julgue a resposta do assistente com base **apenas** nos
                dados do JSON fornecido.  Atribua notas de 0 a 10 para cada critério abaixo
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
        model="o3-mini"
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
    # markdown = load_markdown_content("./assets/relatorio-empresa-1810-fev-mar-abr.md")
    json_data = load_json_content("./assets/relatorio-empresa-1810.json")
    # markdown = load_markdown_content("./assets/relatorio-empresa-1010.md")
    agent = asyncio.run(create_agent_analyst(json_data))
    judge = asyncio.run(create_agent_judge(json_data))
    start_terminal_chat(agent, judge)


if __name__ == "__main__":
    main()