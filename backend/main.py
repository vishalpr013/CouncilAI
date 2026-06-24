# pyrefly: ignore [missing-import]
from app.graph.builder import graph

result = graph.invoke(
    {
        "question":"Should nvidia be a long term investment?"
    }
)

print(result["final_answer"])