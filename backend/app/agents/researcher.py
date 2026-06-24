import re
from app.llm.gemini import llm
from app.tools.financials import get_ticker_data, get_financial_statements
from app.tools.search import search_ticker_news

def researcher(state):
    question = state["question"]
    
    # Extract ticker using LLM for accuracy and reliability
    ticker_extraction = llm.invoke(
        f"Identify the primary publicly traded stock ticker symbol in the following query: '{question}'. "
        "Respond ONLY with the uppercase ticker symbol (e.g. 'AAPL', 'NVDA', 'TSLA'). "
        "If no clear stock or company is mentioned, write 'NONE'."
    )
    ticker = ticker_extraction.content.strip().upper()
    ticker = re.sub(r'[^A-Z]', '', ticker) # Strip any markdown or punctuation

    # Fallback/Default if extraction is none or invalid
    if not ticker or ticker == "NONE" or len(ticker) > 5:
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
    1. The company's recent stock price level, valuation metrics (P/E, PEG), and business summary.
    2. Revenue, Net Income, and Free Cash Flow trends over the past 4 years.
    3. Qualitative factors from recent news.
    
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