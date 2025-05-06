# Agent Facilities

Um agente Python especializado em análise de dados de consumo de espaços flexíveis e reservas empresariais.

## 🚀 Funcionalidades

- Análise de dados de consumo de espaços flexíveis
- Processamento de relatórios em formato Markdown
- Interface de chat via terminal para interação com o agente
- Geração de insights baseados em dados fornecidos

## 📋 Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/tetyemillynha/wai_agent.git
cd agent-python
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```
Edite o arquivo `.env` com suas configurações.

## 🛠️ Dependências

- openai-agents
- python-dotenv

## 📁 Estrutura do Projeto

```
agent-python/
├── .env.example
├── .gitignore
├── README.md
├── agent.py
├── requirements.txt
└── assets/
    └── relatorio-empresa-1810.md
```

## 🚀 Como Usar

1. Certifique-se de que o ambiente virtual está ativado
2. Execute o script principal:
```bash
python agent.py
```

3. Interaja com o agente através do terminal:
   - Digite suas perguntas sobre os dados
   - Digite 'exit' ou 'quit' para sair

## 📝 Notas

- O arquivo `.env` não deve ser versionado
- O diretório `.venv` não deve ser versionado
- Sempre use o `.env.example` como template para configuração