import warnings
from typing import List, Dict, Any

warnings.filterwarnings("ignore", category=RuntimeWarning)
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web using DuckDuckGo.
    Returns a list of dicts: {"title": str, "url": str, "snippet": str}
    """
    results = []
    try:
        ddgs = DDGS()
        raw_results = ddgs.text(query, max_results=max_results)
        for r in raw_results:
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", "")
            })
    except Exception as e:
        # Gracefully handle search failures (e.g. rate limits)
        print(f"Warning: DuckDuckGo search failed for query '{query}': {e}")
    return results
