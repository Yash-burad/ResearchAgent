import httpx
import trafilatura
from bs4 import BeautifulSoup
from typing import Optional

def scrape_url(url: str, timeout: float = 15.0) -> Optional[str]:
    """
    Scrape a webpage and return its main text content.
    Tries trafilatura first, then falls back to httpx + BeautifulSoup.
    """
    # 1. Try Trafilatura extraction
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            content = trafilatura.extract(downloaded, include_links=True, include_comments=False)
            if content and len(content.strip()) > 100:
                return content.strip()
    except Exception as e:
        print(f"Warning: Trafilatura fetch/extract failed for {url}: {e}")

    # 2. Fallback to httpx and BeautifulSoup
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        with httpx.Client(headers=headers, follow_redirects=True, timeout=timeout) as client:
            response = client.get(url)
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, "html.parser")
                
                # Decompose non-content elements
                for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    element.decompose()
                
                # Get clean text
                text = soup.get_text(separator="\n")
                
                # Clean up spacing
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                clean_text = "\n".join(chunk for chunk in chunks if chunk)
                
                if len(clean_text) > 100:
                    return clean_text
    except Exception as e:
        print(f"Warning: BeautifulSoup fallback scraping failed for {url}: {e}")
        
    return None
