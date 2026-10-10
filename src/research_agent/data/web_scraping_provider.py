from typing import List, Dict, Any, Optional
from research_agent.web.search import search_web

class WebScrapingProvider:
    """
    Qualitative market intelligence crawler using DuckDuckGo search for SEC filings,
    press releases, executive commentary, and real-time news events.
    """

    @staticmethod
    def search_stock_news(ticker: str, company_name: str, max_results: int = 15) -> List[Dict[str, Any]]:
        queries = [
            f"{ticker} {company_name} quarterly earnings press release 2026",
            f"{ticker} {company_name} news regulatory product SEC filing",
            f"{company_name} stock catalyst guidance margin commentary"
        ]
        all_results = []
        seen_urls = set()

        for q in queries[:2]:
            results = search_web(q, max_results=max_results)
            for r in results:
                url = r.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append({
                        "title": r.get("title", ""),
                        "url": url,
                        "snippet": r.get("snippet", ""),
                        "source": "Web Search (DDG)"
                    })

        return all_results

    @staticmethod
    def search_competitor_peers(ticker: str, sector: str, industry: str) -> List[Dict[str, Any]]:
        q = f"{ticker} top competitors peers market share {industry}"
        return search_web(q, max_results=5)
