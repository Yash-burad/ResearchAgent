import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from research_agent.models import RefinedTopic, ResearchNotes, ResearchSource
from research_agent.llm import LLMProvider
from research_agent.web import search_web, scrape_url, deduplicate_and_rank_sources

def load_prompt(filename: str) -> str:
    prompts_dir = Path(__file__).parent.parent / "prompts"
    file_path = prompts_dir / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

class ResearcherAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.prompt_template = load_prompt("researcher_agent.md")

    def research_topic(self, topic: RefinedTopic, max_sources: int = 4) -> ResearchNotes:
        """
        Deeply researches a topic by fetching online articles and summarizing them into structured research notes.
        """
        topic_title = topic.title
        
        # 1. Generate search queries
        queries = [
            f'"{topic_title}" official documentation architecture',
            f'"{topic_title}" explained how it works use cases',
            f'"{topic_title}" tradeoffs limitations pros cons'
        ]

        # 2. Search web
        raw_sources = []
        for url in topic.source_urls:
            raw_sources.append({
                "url": url,
                "title": topic_title,
                "snippet": "Initial source URL gathered during topic discovery."
            })
            
        for q in queries:
            results = search_web(q, max_results=3)
            raw_sources.extend(results)

        # 3. Deduplicate and rank
        ranked_sources = deduplicate_and_rank_sources(raw_sources, max_results=max_sources)

        # 4. Scrape the pages
        scraped_data_list = []
        sources_models = []

        for idx, src in enumerate(ranked_sources, 1):
            url = src["url"]
            title = src["title"]
            cred_score = src["credibility_score"]
            
            text_content = scrape_url(url)
            if not text_content:
                text_content = src.get("snippet", "No detailed content extracted.")
            
            # Slice text to stay within local LLM context window limits safely
            sliced_text = text_content[:3500]
            
            scraped_data_list.append(
                f"--- Source {idx} ---\n"
                f"Title: {title}\n"
                f"URL: {url}\n"
                f"Credibility Score: {cred_score}/10\n"
                f"Content:\n{sliced_text}\n"
            )
            
            sources_models.append(
                ResearchSource(
                    url=url,
                    title=title,
                    publisher=None,
                    extracted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    credibility_score=cred_score,
                    key_points=[]
                )
            )

        scraped_sources_str = "\n".join(scraped_data_list)

        # 5. Format prompt and call LLM
        prompt = self.prompt_template.format(
            topic=topic_title,
            scraped_sources=scraped_sources_str
        )

        system_instruction = "You are a meticulous, objective technical researcher who extracts facts and details."

        try:
            notes = self.llm_provider.generate_structured(
                prompt=prompt,
                response_model=ResearchNotes,
                system_instruction=system_instruction
            )
            
            # Fallback: if LLM returned no sources, attach the ones we crawled
            if not notes.sources:
                notes.sources = sources_models
            return notes
        except Exception as e:
            print(f"Warning: ResearcherAgent LLM call failed: {e}. Returning fallback notes.")
            return ResearchNotes(
                topic=topic_title,
                definition=f"A technology trend named {topic_title}.",
                why_it_matters=["Trending software engineering technology", "Relevant for mid-senior technical roles"],
                technical_details=["Detailed notes unavailable due to local model parsing issues."],
                examples=[],
                use_cases=[],
                limitations=[],
                related_topics=[],
                sources=sources_models
            )
