from app.llm.gemini import llm

def reporter(state):
    ticker = state.get("ticker", "AAPL")
    
    reporter_prompt = f"""
    You are the Chairperson of the Investment Committee. Your task is to reconcile the findings of the Researcher, Equity Analyst, and Moat Critic into a single, high-level Executive Report for ticker: {ticker}.
    
    Original Question: {state['question']}
    
    Research Findings:
    {state['research']}
    
    Valuation & DCF Analysis:
    {state['analysis']}
    
    Risk & Moat Critique:
    {state['critique']}
    
    Write a highly professional, balanced Executive Report. The report must contain:
    1. **Executive Summary:** A clear BUY / HOLD / SELL recommendation based on the committee debate.
    2. **Core Valuation Metrics:** Present the current price, computed intrinsic value, and discount target in a neat markdown table.
    3. **Key Growth Drivers:** Highlight the top 2-3 factors supporting the investment.
    4. **Critical Vulnerabilities:** List the top 2-3 risk exposures highlighted by the Critic.
    5. **Consensus Verdict:** A brief concluding statement explaining the committee's final consensus.
    
    Make the report extremely polished, structured, and professional.
    """
    
    result = llm.invoke(reporter_prompt)
    
    return {
        "final_answer": result.content,
        "active_agent": "reporter"
    }
