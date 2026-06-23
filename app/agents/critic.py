# pyrefly: ignore [missing-import]
from app.llm.gemini import llm

def critic(state):
    result = llm.invoke(
        f"""
        Critique and verify:
        {state['analysis']}

        """
    )
    return {
        "critique": result.content
    }