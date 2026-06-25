import re
from app.llm.gemini import llm
from app.tools.financials import get_ticker_data, get_financial_statements
from app.tools.search import search_ticker_news

def researcher(state):
    question = state["question"]
    
    # Extract ticker using LLM for accuracy and reliability
    ticker_extraction = llm.invoke(
        f"Identify the primary publicly traded stock ticker symbol in the following query: '{question}'. "
        "Respond ONLY with the uppercase ticker symbol. For international stocks outside the US (e.g. India, UK), "
        "include the exchange suffix (e.g., '.NS' for NSE India, '.BO' for BSE India, '.L' for London). "
        "Examples: 'WAAREEENER.NS', 'RELIANCE.NS', 'AAPL', 'NVDA'. "
        "If no clear stock or company is mentioned, write 'NONE'."
    )
    ticker = ticker_extraction.content.strip().upper()
    # Strip markdown and standard punctuation, but preserve letters, numbers, and periods for suffixes
    ticker = re.sub(r'[^A-Z0-9\.]', '', ticker)

    # Fallback/Default if extraction is none or invalid
    if not ticker or ticker == "NONE" or len(ticker) > 15:
        ticker = "AAPL" # Default fallback for demo stability

    # Fetch real financial metrics and news
    ticker_data = get_ticker_data(ticker)
    financials = get_financial_statements(ticker)
    news = search_ticker_news(ticker)

    # Prepare detailed context for the researcher agent
    news_snippet = "\n".join([f"- {n['title']}: {n['snippet']} (Source: {n['source']})" for n in news if "error" not in n])
    
    research_prompt = f"""
    You are a Senior Investment Researcher. You have retrieved real-time data for ticker: {ticker}.
    
    Company Profile & Profile Metrics:
    {ticker_data}
    
    Financial Statements History (Past 4 Years):
    {financials}
    
    Recent News & Sentiment:
    {news_snippet}
    
    Based on the retrieved data, write a comprehensive Investment Research Memo for the company.
    In your report, analyze:
    1. The company's recent stock price level, valuation metrics (P/E, PEG), and core business summary (including segment revenues such as networking/software vs. hardware compute if discussed in profile or news).
    2. Revenue, Net Income, and Free Cash Flow trends over the past 4 years. Identify growth drivers or margin pressures.
    3. Supply chain and manufacturing profile: Highlight single-source dependencies (e.g., TSMC or advanced packaging bottlenecks) and manufacturing locations.
    4. Geopolitical and regulatory risks: Specifically note export controls (such as restrictions on China) or other compliance/legal constraints.
    5. Qualitative factors from recent news and market sentiment.
    
    Provide a well-structured Markdown report. Do not calculate the DCF value yourself; the Valuation Analyst will compute it programmatically.
    """
    
    result = llm.invoke(research_prompt)
    
    return {
        "ticker": ticker,
        "raw_financials": financials if "error" not in financials else {},
        "news_summary": news if isinstance(news, list) else [],
        "research": result.content,
        "active_agent": "researcher"
    }