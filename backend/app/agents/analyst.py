from app.llm.gemini import llm
from app.tools.financials import calculate_dcf

def analyst(state):
    ticker = state.get("ticker", "AAPL")
    
    # Run programmatic DCF valuation
    dcf_result = calculate_dcf(
        ticker=ticker,
        revenue_growth=0.10,      # Default 10%
        discount_rate=0.09,       # Default 9%
        terminal_multiple=15.0,   # Default 15x
        margin_of_safety=0.20     # Default 20%
    )
    
    analysis_prompt = f"""
    You are a Senior Equity Valuation Analyst. You have run a Discounted Cash Flow (DCF) model for ticker: {ticker}.
    
    Programmatic DCF Model Output:
    {dcf_result}
    
    Context from Research Memo:
    {state['research']}
    
    Based on the programmatic model output and the research details:
    1. Summarize the intrinsic value computed (${dcf_result.get('intrinsic_value', 0):.2f}) relative to the current stock price (${dcf_result.get('current_price', 0):.2f}).
    2. Discuss the growth assumptions (10% growth) compared to the company's historical metrics.
    3. Outline the target buying price (incorporating a 20% Margin of Safety).
    4. Provide your overall Analyst Recommendation (e.g., BUY, HOLD, or SELL).
    
    Write your analysis clearly in Markdown.
    """
    
    result = llm.invoke(analysis_prompt)
    
    return {
        "dcf_valuation": dcf_result,
        "analysis": result.content,
        "active_agent": "analyst"
    }