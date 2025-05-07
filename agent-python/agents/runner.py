class Runner:
    @staticmethod
    async def run(agent, question: str):
        prompt = f"{agent.instructions}\n\nPergunta: {question}"
        response = await agent.model.ask(prompt)
        return type("Result", (), {"final_output": response})()