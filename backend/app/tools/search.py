from duckduckgo_search import DDGS
from typing import List, Dict, Any

def search_ticker_news(ticker: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Searches DuckDuckGo for recent news and info about a ticker symbol."""
    try:
        query = f"${ticker.upper()} stock financial news analysis"
        results = []
        with DDGS() as ddgs:
            for r in ddgs.news(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url": r.get("url", ""),
                    "source": r.get("source", ""),
                    "date": r.get("date", "")
                })
        return results
    except Exception as e:
        # Fallback to text search if news search fails or is rate-limited
        try:
            query = f"{ticker.upper()} stock financial news"
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "snippet": r.get("body", ""),
                        "url": r.get("href", ""),
                        "source": "Web Search",
                        "date": "Recent"
                    })
            return results
        except Exception as ex:
            return [{"error": f"Search failed: {str(ex)}"}]
