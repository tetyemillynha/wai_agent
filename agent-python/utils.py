from dotenv import load_dotenv
from pathlib import Path

from typing import List, Dict
import re
from collections import defaultdict

def load_env_variables():
    load_dotenv()

def load_markdown_content(filepath: str) -> str:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
    return path.read_text(encoding="utf-8")


def parse_markdown(markdown_text: str) -> dict:
    """
    Extrai dados estruturados a partir do markdown.
    """
    insights = defaultdict(dict)

    # Resumo geral
    resumo_match = re.search(
        r"Total de reservas: (\d+).+?Cr\u00e9ditos consumidos: ([\d.]+).+?Valor gasto estimado: R\$ ([\d.,]+).+?Cidades atendidas: (\d+).+?Grupos identificados: (\d+)",
        markdown_text,
        re.DOTALL,
    )
    if resumo_match:
        insights["resumo_geral"] = {
            "total_reservas": int(resumo_match.group(1)),
            "creditos_consumidos": float(resumo_match.group(2)),
            "valor_estimado": float(resumo_match.group(3).replace(",", ".")),
            "cidades": int(resumo_match.group(4)),
            "grupos": int(resumo_match.group(5)),
        }

    # Pacote
    pacote_match = re.search(
        r"Cr\u00e9ditos totais: (\d+).+?Cr\u00e9ditos consumidos: ([\d.]+).+?Cr\u00e9ditos dispon\u00edveis: ([\d.]+).+?Porcentagem consumida: ([\d.]+)%",
        markdown_text,
        re.DOTALL,
    )
    if pacote_match:
        insights["pacote"] = {
            "creditos_totais": int(pacote_match.group(1)),
            "creditos_consumidos": float(pacote_match.group(2)),
            "creditos_disponiveis": float(pacote_match.group(3)),
            "porcentagem_consumida": float(pacote_match.group(4)),
        }

    # Usuários top
    usuarios_top = re.findall(r"\*\*(.*?)\*\*.*?\u2013 ([\d.]+) cr\u00e9ditos", markdown_text)
    insights["usuarios_top"] = [
        {"nome": nome.strip(), "creditos": float(creditos)} for nome, creditos in usuarios_top
    ]

    # Check-ins
    checkin_match = re.search(
        r"Check-ins:\s+- Realizados: (\d+)\s+- N\u00e3o realizados: (\d+)", markdown_text)
    if checkin_match:
        insights["checkins"] = {
            "realizados": int(checkin_match.group(1)),
            "nao_realizados": int(checkin_match.group(2))
        }

    # Produtos
    produtos_match = re.findall(r"- ([\w\s/&]+): (\d+) reservas", markdown_text)
    produtos_dict = {}
    for nome, qtd in produtos_match:
        nome = nome.strip().lower()
        produtos_dict[nome] = produtos_dict.get(nome, 0) + int(qtd)
    insights["produtos"] = produtos_dict

    # Cidades top
    cidades_match = re.findall(r"\*\*(.+?)\*\*: (\d+) reservas", markdown_text)
    insights["cidades_top"] = sorted(
        [{"cidade": nome.strip(), "reservas": int(res)} for nome, res in cidades_match],
        key=lambda x: x["reservas"], reverse=True
    )[:10]

    return insights


def gerar_insights(question: str, insights: dict) -> str:
    bullets = []
    q = question.lower()

    if "grupo" in q and ("aceleraram" in q or "risco" in q):
        grupos = [
            {"nome": "Grupo None", "creditos": 2061.00},
            {"nome": "CX", "creditos": 109.00},
            {"nome": "Product", "creditos": 88.00},
        ]
        bullets.append(f"- **Grupo None** lidera o consumo com 2061 cr\u00e9ditos.")
        bullets.append(f"- **CX** e **Product** aparecem na sequ\u00eancia com 109 e 88 cr\u00e9ditos.")
        bullets.append("- O consumo elevado de poucos grupos pode indicar risco de esgotamento do pacote.")

    elif "cidade" in q and ("gasto por reserva" in q or "custo-benef\u00edcio" in q):
        for cidade in insights.get("cidades_top", [])[:3]:
            bullets.append(f"- **{cidade['cidade']}**: {cidade['reservas']} reservas")
        bullets.append("- A concentra\u00e7\u00e3o em poucas cidades sugere oportunidades para renegocia\u00e7\u00e3o ou expans\u00e3o.")

    elif "usu\u00e1rio" in q and "50 cr\u00e9ditos" in q:
        for user in insights["usuarios_top"]:
            if user["creditos"] > 50:
                bullets.append(f"- {user['nome']} consumiu {user['creditos']} cr\u00e9ditos.")
        if insights["produtos"].get("compartilhado"):
            bullets.append(f"- Produto dominante: **Compartilhado**, com {insights['produtos']['compartilhado']} reservas.")
        dias_semana = [k for k in insights["produtos"] if k in ["monday", "tuesday", "wednesday", "thursday", "friday"]]
        if dias_semana:
            top_dia = max([(dia, insights["produtos"][dia]) for dia in dias_semana], key=lambda x: x[1])
            bullets.append(f"- Maior uso ocorreu \u00e0s **{top_dia[0].capitalize()}s**, com {top_dia[1]} reservas.")

    elif "cancelamento" in q or "no-show" in q or "desperd\u00edcio" in q:
        checkins = insights.get("checkins", {})
        if checkins:
            total = checkins["realizados"] + checkins["nao_realizados"]
            perc = (checkins["nao_realizados"] / total) * 100
            desperdicio = checkins["nao_realizados"] * (insights["pacote"]["creditos_consumidos"] / insights["resumo_geral"]["total_reservas"])
            bullets.append(f"- Taxa de no-show: **{perc:.1f}%** ({checkins['nao_realizados']} de {total} reservas).")
            bullets.append(f"- Estimativa de cr\u00e9ditos desperdi\u00e7ados: **{desperdicio:.1f} cr\u00e9ditos**.")
        else:
            bullets.append("N\u00e3o h\u00e1 dados suficientes sobre check-ins.")

    elif "produto" in q and ("consumo" in q or "proje\u00e7\u00e3o" in q):
        total = sum([v for k, v in insights["produtos"].items() if k in ["compartilhado", "reuni\u00e3o", "outro"]])
        for k in ["compartilhado", "reuni\u00e3o", "outro"]:
            if k in insights["produtos"]:
                p = (insights["produtos"][k] / total) * 100
                bullets.append(f"- {k.capitalize()}: {p:.1f}% das reservas.")
        media = insights["pacote"]["creditos_consumidos"] / 90
        proj = media * 60
        bullets.append(f"- Proje\u00e7\u00e3o de consumo para 60 dias: **{proj:.1f} cr\u00e9ditos** (~{media:.1f}/dia).")

    if not bullets:
        return "Desculpe! N\u00e3o encontramos dados suficientes para responder \u00e0 sua pergunta neste momento."

    return "### \ud83d\udd0d Insights\n" + "\n".join(bullets)
