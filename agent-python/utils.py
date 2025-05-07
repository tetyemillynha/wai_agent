from dotenv import load_dotenv
from pathlib import Path

def load_env_variables():
    load_dotenv()

def load_markdown_content(filepath: str) -> str:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
    return path.read_text(encoding="utf-8")
