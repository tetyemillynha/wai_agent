from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from utils import load_env_variables, load_json_content
from main import create_agent_analyst, handle_question, create_agent_judge, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered, create_graph_classifier_agent
# from charts import create_chart_top_users, extract_top_users_from_markdown
import os

load_env_variables()

app = FastAPI(title="WAi Facilities API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://local.woba.com.br:3000",
        "https://feat-ped-7107.new-myoffice.staging.woba.com.br"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

json_data = load_json_content("./assets/relatorio-empresa-1810.json")

class QuestionPayload(BaseModel):
    question: str

@app.post("/chat")
async def chat_agent(payload: QuestionPayload):
    try:
        agent, markdown = await create_agent_analyst(json_data, payload.question)
        resposta = await handle_question(agent, payload.question)

        graph_classifier_agent = await create_graph_classifier_agent()
        result = await handle_question(graph_classifier_agent, resposta)

        can_generate = result.strip().upper() == "GRAFICO_POSSIVEL"

        if can_generate:
            resposta += "\n\n📊 Gostaria que eu gerasse os gráficos desses insights?"

        # judge = await create_agent_judge(markdown)
        # prompt_judge = f"""
        #     QUESTION:
        #     {payload.question}

        #     ANSWER:
        #     {resposta}
        # """
        # julgamento = await handle_question(judge, prompt_judge)

        return {
            "resposta": resposta.strip(),
            # "avaliacao": julgamento
        }
    except InputGuardrailTripwireTriggered as e:
        return {
            "erro": "422",
            "mensagem": "Pergunta fora do escopo"
        }

    except OutputGuardrailTripwireTriggered as e:
        # print(f"📋 Output Guardrail Result: {e.output_info}")
        return {
            "erro": "422",
            "mensagem": "Resposta reprovada pelo guardrail de formato"
        }

    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

# app.mount("/static", StaticFiles(directory="static"), name="static")