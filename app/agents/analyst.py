# pyrefly: ignore [missing-import]
from app.llm.gemini import llm

def analyst(state):
    result = llm.invoke(
        f"""
        Analyse:
        {state['research']}
        """
    )
    return {
        "analysis": result.content
    }