from app.llm.gemini import llm
from app.tools.financials import calculate_dcf, get_ticker_data
import json

def analyst(state):
    ticker = state.get("ticker", "AAPL")
    
    # 1. Fetch raw financials and ticker data
    raw_financials = state.get("raw_financials", {})
    ticker_data = get_ticker_data(ticker)
    
    # 2. Estimate historical CAGR
    hist_revenue = raw_financials.get("revenue", [])
    
    growth_info = ""
    if len(hist_revenue) >= 2:
        cagrs = []
        for i in range(len(hist_revenue)-1):
            if hist_revenue[i] > 0:
                cagrs.append((hist_revenue[i+1] - hist_revenue[i]) / hist_revenue[i])
        avg_hist_growth = sum(cagrs) / len(cagrs) if cagrs else 0.10
        growth_info = f"Historical annual revenue growth rates over the last {len(hist_revenue)} years: " + ", ".join([f"{g*100:.1f}%" for g in cagrs]) + f" (Average: {avg_hist_growth*100:.1f}%)."
    else:
        avg_hist_growth = 0.10
        growth_info = "Historical financial history is too brief to calculate CAGR."
    
    # 3. Query LLM to determine DCF assumptions based on history and risk profile
    estimation_prompt = f"""
    You are a Senior Equity Research Director. Determine realistic, professional Discounted Cash Flow (DCF) assumptions for ticker: {ticker}.
    
    Company Profile & Metrics:
    {ticker_data}
    
    Historical Growth Context:
    {growth_info}
    
    Based on the industry, beta, growth profile, and historical performance, output the following DCF inputs:
    1. Expected annual revenue growth rate for the next 5 years (revenue_growth) - typically between 0.05 (5%) and 0.40 (40%). For high-growth leaders like NVDA, do not use a generic low number if historical growth is very high. Be realistic but moderate hyper-growth.
    2. Discount Rate / WACC (discount_rate) - typically between 0.07 (7%) and 0.15 (15%) based on the company's beta, leverage, and industry risk.
    3. Terminal EV/FCF Multiple (terminal_multiple) - typically between 10.0 and 35.0 based on competitive moat and growth durability.
    4. Margin of Safety (margin_of_safety) - typically 0.10 (10%), 0.15 (15%), or 0.20 (20%) based on predictability.
    
    Respond ONLY with a JSON object in this format:
    {{
        "revenue_growth": 0.25,
        "discount_rate": 0.11,
        "terminal_multiple": 25.0,
        "margin_of_safety": 0.15,
        "rationale": "Brief 1-sentence rationale for these parameters."
    }}
    Do not add any markdown formatting, wrappers, or backticks around the JSON.
    """
    
    # Call LLM for dynamic assumptions
    est_response = llm.invoke(estimation_prompt)
    content = est_response.content.strip()
    
    if content.startswith("```"):
        lines = content.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines).strip()
        
    try:
        assumptions = json.loads(content)
        rev_growth = float(assumptions.get("revenue_growth", 0.10))
        disc_rate = float(assumptions.get("discount_rate", 0.09))
        term_mult = float(assumptions.get("terminal_multiple", 15.0))
        mos = float(assumptions.get("margin_of_safety", 0.20))
        rationale = assumptions.get("rationale", "Defaults applied.")
    except Exception as e:
        rev_growth = 0.10
        disc_rate = 0.09
        term_mult = 15.0
        mos = 0.20
        rationale = f"Parsing failed ({str(e)}), fell back to defaults."
    
    # Run programmatic DCF valuation
    dcf_result = calculate_dcf(
        ticker=ticker,
        revenue_growth=rev_growth,
        discount_rate=disc_rate,
        terminal_multiple=term_mult,
        margin_of_safety=mos
    )
    
    # Add assumptions to the result for reporter visibility
    dcf_result["revenue_growth"] = rev_growth
    dcf_result["discount_rate"] = disc_rate
    dcf_result["terminal_multiple"] = term_mult
    dcf_result["rationale"] = rationale
    
    analysis_prompt = f"""
    You are a Senior Equity Valuation Analyst. You have run a Discounted Cash Flow (DCF) model for ticker: {ticker}.
    
    Programmatic DCF Model Output:
    {dcf_result}
    
    Context from Research Memo:
    {state['research']}
    
    Based on the programmatic model output and the research details:
    1. Summarize the intrinsic value computed (${dcf_result.get('intrinsic_value', 0):.2f}) relative to the current stock price (${dcf_result.get('current_price', 0):.2f}).
    2. Discuss and justify the growth assumption ({rev_growth*100:.1f}%), discount rate ({disc_rate*100:.1f}%), and terminal multiple ({term_mult:.1f}x) used, citing the historical averages and risk factors.
    3. Outline the target buying price (incorporating a {mos*100:.1f}% Margin of Safety: ${dcf_result.get('buy_price_target', 0):.2f}).
    4. Provide your overall Analyst Recommendation (e.g., BUY, HOLD, or SELL).
    
    Write your analysis clearly in Markdown.
    """
    
    result = llm.invoke(analysis_prompt)
    
    return {
        "dcf_valuation": dcf_result,
        "analysis": result.content,
        "active_agent": "analyst"
    }