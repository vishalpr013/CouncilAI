from app.llm.gemini import llm

def critic(state):
    ticker = state.get("ticker", "AAPL")
    
    critique_prompt = f"""
    You are an Independent Risk Manager and Moat Critic. Your job is to poke holes in the investment thesis for ticker: {ticker}.
    
    Research Memo:
    {state['research']}
    
    Analyst Valuation Summary:
    {state['analysis']}
    
    Provide an adversarial audit of the proposed buy case:
    1. Highlight structural risks: Is the valuation model too aggressive? What happens if growth slows down?
    2. Analyze the balance sheet strength: Check debt burden, asset coverage, and interest rate sensitivity.
    3. Discuss competitive threats (Moat analysis): Is the company losing its edge? Are competitors gaining share?
    4. Construct a clear Bear Case for this investment.
    
    Present your risk critique in clean, structured Markdown.
    """
    
    result = llm.invoke(critique_prompt)
    
    return {
        "critique": result.content,
        "active_agent": "critic"
    }