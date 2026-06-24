from typing import TypedDict, Dict, Any, List

class AgentState(TypedDict):
    question: str
    ticker: str
    raw_financials: Dict[str, Any]
    dcf_valuation: Dict[str, Any]
    news_summary: List[Dict[str, Any]]
    research: str
    analysis: str
    critique: str
    final_answer: str
    active_agent: str