import asyncio
from agents import (
    Agent,
    Runner,
    GuardrailFunctionOutput,
    InputGuardrail,
    input_guardrail,
    OutputGuardrail,
    output_guardrail,
    RunContextWrapper,
    TResponseInputItem,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered
)
from utils import load_env_variables, load_json_content

async def create_agent_guardrail(name: str, instructions: str) -> Agent:
    return Agent(
        name=name,
        instructions=instructions,
        model="gpt-4o-mini",
    )

@input_guardrail
async def check_input_guardrail(
    ctx: RunContextWrapper[None],
    _: Agent,
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    guardrail_agent = await create_agent_guardrail(
        name="Input Guardrail Agent",
        instructions=(
            f"""
                Você é um verificador de escopo.
                Responda apenas PASS ou FAIL.

                1. Fala sobre consumo de créditos, reservas ou pacotes de espaços flexíveis da empresa?  
                2. Está em português e contém um pedido claro?  
                3. Não pede dados pessoais sensíveis nem informações fora do escopo?

                Se TODAS as respostas forem "sim", responda apenas com PASS.  
                Caso contrário, responda apenas com FAIL e NÃO acrescente nada além dessa palavra.
            """
        )
    )
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.strip() == "FAIL"
    )

@output_guardrail
async def check_output_guardrail(
    ctx: RunContextWrapper[None],
    _: Agent,
    response_agent: str
) -> GuardrailFunctionOutput:
    guardrail_agent = await create_agent_guardrail(
        name="Output Guardrail Agent",
        instructions=(
            f"""
                Você é um auditor de formato de saída.
                Responda apenas PASS ou FAIL.

                Critérios (todos obrigatórios):

                ✓ A resposta é em português.  
                ✓ Contém de 3 a 5 bullet points iniciados por "- " (travessão + espaço).  
                ✓ Cada bullet é curto, direto e usa linguagem acessível a gestores.  
                ✓ Não há jargões técnicos, links, cabeçalhos ou emojis.  
                ✓ Não menciona "dados insuficientes" **a menos** que a resposta inteira seja exatamente:
                "Desculpe! Não encontramos dados suficientes para responder à sua pergunta neste momento."

                Se TODOS os critérios forem atendidos, devolva apenas PASS.  
                Caso qualquer critério falhe, devolva apenas FAIL.
            """
        )
    )
    result = await Runner.run(guardrail_agent, response_agent, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.strip() == "FAIL"
    )

async def create_agent_analyst(markdown_data: str) -> Agent:
    return Agent(
        name="Booking Report Analyst",
        instructions=(
            f"""
                Você é um analista de dados especializado em consumo de espaços flexíveis e reservas empresariais.

                Contexto:
                - Dados da empresa (JSON): {markdown_data}

                Instruções:
                1. Baseie-se exclusivamente nos dados acima — não invente nada.
                2. Gere de 3 a 5 insights em bullet points:
                - Seja direto e claro.
                - Destaque padrões, aumentos ou quedas relevantes.
                - Evite jargões técnicos; linguagem acessível a gestores.
                - Indique limitações de forma sutil, sem pedir mais dados.
                3. Se os dados forem insuficientes: retorne exatamente
                "Desculpe! Não encontramos dados suficientes para responder à sua pergunta neste momento."
                4. Se o usuário apenas agradecer, responda de forma amigável e não forneça insights.
                5. Não adicione cabeçalhos, emojis ou assinaturas — apenas os bullets (ou a mensagem de desculpas).
            """
        ),
        model="litellm/anthropic/claude-3-5-sonnet-20240620",
        input_guardrails=[check_input_guardrail],
        output_guardrails=[check_output_guardrail]
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
        model="o3"
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

            try:
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

            except InputGuardrailTripwireTriggered:
                print("❌ Desculpe, sua pergunta está fora do escopo do assistente. Por favor, faça uma pergunta relacionada a:")
                print("- Consumo de créditos")
                print("- Reservas empresariais")
                print("- Uso de espaços flexíveis")
                print("- Tendências por grupo, cidade ou usuário")
                print("- Comparativos entre períodos")
                print("- Informações baseadas em relatórios de uso")
                print()
            except OutputGuardrailTripwireTriggered:
                print("Desculpe! Algo deu errado ao gerar a resposta.")

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