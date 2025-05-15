import asyncio
from agents import Agent, Runner, ModelSettings
from utils import load_env_variables, load_json_content

gpt_instructions = """
Você é um analista de dados experiente. Responda com precisão e evite inferências que não estejam diretamente sustentadas pelos dados.

Você receberá:
1. Uma pergunta em linguagem natural, já validada e dentro do escopo
2. Um documento em Markdown (markdown estruturado) com os dados da empresa

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

Você receberá:
1. Uma pergunta em linguagem natural, já validada e dentro do escopo
2. Um documento em Markdown (markdown estruturado) com os dados da empresa

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

sonnet_3_7_instructions = """
Você é um analista de dados sênior. Sua tarefa é gerar uma resposta objetiva, útil e visualmente organizada com base **somente nos dados fornecidos**.

Você receberá:
1. Uma pergunta em linguagem natural, já validada e dentro do escopo
2. Um documento em Markdown (markdown estruturado) com os dados da empresa

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

async def create_agent_analyst(json_data: str, user_question: str) -> Agent:
    model = "litellm/anthropic/claude-3-5-sonnet-20240620"
    # model = "litellm/anthropic/claude-3-7-sonnet-20250219"
    # model = "gpt-4o"


    # Gera relatório com base na pergunta real
    generate_agent = create_generate_report_agent(json_data, user_question)
    markdown_report = await handle_question(generate_agent, user_question)

    print(f"🔍 Relatório gerado: {markdown_report}")
    

    # 3.5 não ficou legal ajustando os parâmetros
    model_settings_sonnet_3_5 = ModelSettings(
        temperature=0.1,
        top_p=1,
        max_tokens=2500
    )

    model_settings_sonnet_3_7 = ModelSettings(
        temperature=0.1,
        top_p=1,
        max_tokens=3000
    )

    model_settings_gpt_4o = ModelSettings(
        temperature=0.1,
        top_p=1,
        max_tokens=3000,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    agent = Agent(
        name="Booking Report Analyst",
        instructions=(
            f"""
            {sonnet_3_5_instructions}

            Dados do relatório:
            {markdown_report}
            """
        ),
        model=model,
        model_settings=model_settings_sonnet_3_5
    )

    return agent, markdown_report

async def create_agent_judge(markdown_data: str) -> Agent:
    return Agent(
        name="Agent Judge",
        instructions=(
            f"""
                Você é um avaliador rigoroso.  Julgue a resposta do assistente com base **apenas** nos
                dados do Markdown fornecido.  Atribua notas de 0 a 10 para cada critério abaixo
                (exatidão, relevância, clareza_formato, insight).

                Retorne **somente** o Markdown no formato:

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
                - Nunca inclua explicações fora do Markdown.

                Dados do relatório:
                {markdown_data}
            """
        ),
        model="o3-mini"
    )

async def handle_question(agent: Agent, question: str):
    result = await Runner.run(agent, question)
    return result.final_output

def start_terminal_chat(json_data: str):
    print("💬 Chat inicializado com o Agente Facilities (digite 'exit' para sair)\n")

    async def chat_loop():
        while True:
            user_input = input("Usuário: ")
            if user_input.lower() in {"exit", "quit"}:
                print("👋 Saindo do chat.")
                break

            # 1. Cria agent e obtém o relatório em markdown
            agent, markdown_report = await create_agent_analyst(json_data, user_input)

            # 2. Roda o agente com a pergunta
            response = await handle_question(agent, user_input)
            print(f"\n🤖 Agente Facilities:\n{response}\n")

            # 3. Cria o juiz com o markdown, não com o JSON original
            judge = await create_agent_judge(markdown_report)

            # 4. Avaliação
            if judge:
                prompt_judge = f"""
                    QUESTION:
                    {user_input}

                    ANSWER:
                    {response}
                """
                judge_response = await handle_question(judge, prompt_judge)
                print(f"🧑‍⚖️ Agente Judge:\n{judge_response}\n")

    asyncio.run(chat_loop())

def main():
    load_env_variables()
    json_data = load_json_content("./assets/relatorio-empresa-1810.json")
    
    start_terminal_chat(json_data)

def create_generate_report_agent(json_data: str, question: str):
    model = "gpt-4o"
    model_settings_gpt_4o = ModelSettings(
        temperature=0.1,
        top_p=1,
        max_tokens=3000,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    generate_report_instructions = """
        Você é um analista de dados experiente. Sua missão é gerar um relatório analítico **somente quando a pergunta estiver relacionada ao uso de créditos, reservas, espaços, consumo ou análise de comportamento dos usuários**.

        Você recebeu a seguinte pergunta do usuário:
        "{question}"

        ### Regras:
        - Se a pergunta for um agradecimento, cumprimento ou algo fora do contexto esperado, **não gere nenhum relatório** e simplesmente retorne:
        > "{}"

        Com base apenas nos dados do JSON abaixo, gere um relatório completo com os principais insights que ajudam a responder a essa pergunta.

        Dados do relatório:
        {json_data}

        O relatório deve ser em **markdown bem formatado**, com seções, listas e títulos claros, facil de ser lido e interpretado por outros analistas.
    """

    return Agent(
        name="Generate Report Agent",
        instructions=(
            f"""
            {generate_report_instructions}

            Dados do relatório:
            {json_data}
            """
        ),
        model=model,
        model_settings=model_settings_gpt_4o
    )


if __name__ == "__main__":
    main()