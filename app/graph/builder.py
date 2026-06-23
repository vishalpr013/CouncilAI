from langgraph.graph import StateGraph
# pyrefly: ignore [missing-import]
from app.graph.state import AgentState
# pyrefly: ignore [missing-import]
from app.agents.researcher import researcher
# pyrefly: ignore [missing-import]
from app.agents.analyst import analyst
# pyrefly: ignore [missing-import]
from app.agents.critic import critic
# pyrefly: ignore [missing-import]
from app.agents.reporter import reporter

builder = StateGraph(AgentState)

builder.add_node("researcher",researcher)
builder.add_node("analyst", analyst)
builder.add_node("critic", critic)
builder.add_node("reporter", reporter)

builder.set_entry_point("researcher")

builder.add_edge("researcher","analyst")
builder.add_edge("analyst","critic")
builder.add_edge("critic","reporter")

graph = builder.compile()