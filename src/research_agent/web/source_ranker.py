from urllib.parse import urlparse
from typing import List, Dict, Any

def get_domain(url: str) -> str:
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return ""

def score_source_credibility(url: str) -> int:
    """
    Returns a score from 1 to 10 based on the domain credibility.
    """
    domain = get_domain(url)
    if not domain:
        return 3

    # 1. High credibility: Official docs, standards, major cloud, Github official
    high_domains = [
        "github.com", "w3.org", "ietf.org", "rfc-editor.org",
        "aws.amazon.com", "cloud.google.com", "azure.microsoft.com",
        "kubernetes.io", "docker.com", "hashicorp.com", "redis.io",
        "postgresql.org", "apache.org", "mozilla.org", "developer.mozilla.org",
        "openai.com", "anthropic.com", "google.ai", "microsoft.com", "oracle.com"
    ]
    for d in high_domains:
        if domain == d or domain.endswith("." + d):
            return 9

    # 2. Medium-High credibility: Renowned engineering blogs and reputable tech publishers
    med_high_domains = [
        "netflixtechblog.com", "engineering.linkedin.com", "uber.com/blog", 
        "cloudflare.com", "martinfowler.com", "thoughtworks.com",
        "infoq.com", "medium.com/engineering", "blog.cloudflare.com",
        "arxiv.org", "nature.com", "ieee.org"
    ]
    for d in med_high_domains:
        if d in domain or domain.endswith("." + d):
            return 8

    # 3. Medium credibility: Curated news/portals
    med_domains = [
        "techcrunch.com", "theverge.com", "wired.com", "zdnet.com", "venturebeat.com",
        "news.ycombinator.com", "github.blog", "medium.com", "dev.to"
    ]
    for d in med_domains:
        if domain == d or domain.endswith("." + d):
            return 6

    # Default/Unknown domain
    return 5

def deduplicate_and_rank_sources(sources: List[Dict[str, Any]], max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Deduplicates sources by URL and Title (case-insensitive), scores them by credibility,
    and returns the top N ranked by credibility.
    """
    seen_urls = set()
    seen_titles = set()
    unique_sources = []

    for src in sources:
        url = src.get("url", "").strip()
        title = src.get("title", "").strip().lower()
        if not url:
            continue
        
        # Normalize URL
        norm_url = url.split("?")[0].rstrip("/")
        
        if norm_url in seen_urls or (title and title in seen_titles):
            continue
            
        seen_urls.add(norm_url)
        if title:
            seen_titles.add(title)
            
        cred_score = score_source_credibility(url)
        
        unique_sources.append({
            "title": src.get("title", ""),
            "url": url,
            "snippet": src.get("snippet", ""),
            "credibility_score": cred_score
        })

    # Sort by credibility score descending, then return top max_results
    unique_sources.sort(key=lambda x: x["credibility_score"], reverse=True)
    return unique_sources[:max_results]
