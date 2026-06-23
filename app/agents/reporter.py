# pyrefly: ignore [missing-import]
from app.llm.gemini import llm
from app.agents.researcher import researcher
from app.agents.analyst import analyst
from app.agents.critic import critic

def reporter(state):
    result = llm.invoke(
        f"""
        Based on the following research and analysis, write a concise, clear, and well-structured report that answers the user's question:

        Research:
        {state['research']}

        Analysis:
        {state['analysis']}

        Critique:
        {state['critique']}

        Question: {state['question']}
        """
    )
    return {"final_answer": result.content}
