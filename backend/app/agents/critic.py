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
    1. Highlight structural risks: Is the valuation model too aggressive? What happens if growth slows down? How sensitive is the valuation to changes in interest rates/WACC?
    2. Analyze balance sheet and resource limits: Check interest rate sensitivity, debt levels, and physical limits (like data center power grid capacity constraints and physical footprint ceilings).
    3. Discuss real competitive threats (Moat analysis): Focus on custom hyperscaler silicon (e.g., Google TPUs, AWS Trainium, MS Maia, Meta MTIA) bypassing the vendor stack entirely. 
       *Note: Avoid shallow statements like 'PyTorch/Triton erode CUDA's moat' since these frameworks are highly optimized for and run directly on CUDA today. Instead, focus on architectural or hardware alternatives.*
    4. Supply Chain Vulnerabilities: Critique dependencies on single-source suppliers (e.g., TSMC fabrication, advanced packaging bottlenecks like CoWoS) and export compliance risks.
    5. Construct a clear Bear Case for this investment.
    
    Present your risk critique in clean, structured Markdown.
    """
    
    result = llm.invoke(critique_prompt)
    
    return {
        "critique": result.content,
        "active_agent": "critic"
    }