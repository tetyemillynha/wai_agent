# charts.py
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import re

def create_chart_top_users(df: pd.DataFrame, save_dir="static", company_name: str = "Recargapay"):
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, y="Nome", x="Créditos Consumidos", palette="viridis")
    plt.title(f"Top Usuários por Consumo de Créditos - {company_name}")
    plt.xlabel("Créditos Consumidos")
    plt.ylabel("Usuário")
    plt.tight_layout()

    os.makedirs(save_dir, exist_ok=True)
    filename = f"top_usuarios_{company_name}_{datetime.now().timestamp()}.png"
    filepath = os.path.join(save_dir, filename)
    plt.savefig(filepath)
    plt.close()
    return filepath


def extract_top_users_from_markdown(md: str) -> pd.DataFrame:
    blocos = re.findall(r"- \*\*(.+?)\*\*: (\d+) reservas, (\d+(?:\.\d+)?) créditos", md)
    return pd.DataFrame(blocos, columns=["Nome", "Reservas", "Créditos Consumidos"]).astype({
        "Reservas": int,
        "Créditos Consumidos": float
    })

