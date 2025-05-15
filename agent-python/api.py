from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils import load_env_variables, load_json_content
from main import create_agent_analyst, handle_question, create_agent_judge, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered
load_env_variables()

app = FastAPI(title="WAi Facilities API")

json_data = load_json_content("./assets/relatorio-empresa-1810.json")

class QuestionPayload(BaseModel):
    question: str

@app.post("/chat")
async def chat_agent(payload: QuestionPayload):
    try:
        agent, markdown = await create_agent_analyst(json_data, payload.question)
        resposta = await handle_question(agent, payload.question)

        judge = await create_agent_judge(markdown)
        prompt_judge = f"""
            QUESTION:
            {payload.question}

            ANSWER:
            {resposta}
        """
        julgamento = await handle_question(judge, prompt_judge)

        return {
            "resposta": resposta.strip(),
            "avaliacao": julgamento
        }
    except InputGuardrailTripwireTriggered as e:
        print(f"🔍 Input Guardrail Result: {e}")
        return {
            "erro": "Pergunta fora do escopo",
            "tipo": e.output_info,
            "mensagem": "Por favor, pergunte algo relacionado a consumo de créditos, reservas, usuários, grupos, cidades ou espaços utilizados."
        }

    except OutputGuardrailTripwireTriggered as e:
        return {
            "erro": "Resposta reprovada pelo guardrail de formato",
            "tipo": e.output_info,
            "mensagem": "A estrutura da resposta não está no formato esperado. Estamos corrigindo isso."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))