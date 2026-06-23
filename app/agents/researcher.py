# pyrefly: ignore [missing-import]
from app.llm.gemini import llm

def researcher(state):
    question = state["question"]

    result = llm.invoke(
        f"""Perform deep research on the given topic '{question}'. Provide detailed, accurate, 
        and comprehensive information based on up-to-date knowledge. Include relevant facts, figures, and insights. 
        Your response should be well-structured and easy to understand."""
    )
    return {"research": result.content}