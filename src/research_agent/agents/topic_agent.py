import os
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel
from research_agent.models import TopicCandidate
from research_agent.llm import LLMProvider
from research_agent.web import search_web

class TopicCandidatesList(BaseModel):
    topics: List[TopicCandidate]

def load_prompt(filename: str) -> str:
    prompts_dir = Path(__file__).parent.parent / "prompts"
    file_path = prompts_dir / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

class TopicAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.prompt_template = load_prompt("topic_agent.md")

    def discover_topics(self, user_interests: str, max_candidates: int = 15) -> List[TopicCandidate]:
        """
        Discovers trending topics related to user interests by searching the web and using LLM analysis.
        """
        interests_list = [i.strip() for i in user_interests.split(",") if i.strip()]
        
        # Build search queries
        queries = ["emerging technology trends software engineering 2026"]
        for interest in interests_list[:3]:  # Limit interest categories to keep query count low
            queries.append(f"trending technology {interest} 2026")
            queries.append(f"new developer tools architecture {interest}")

        # Execute searches and collect results
        search_results_compiled = []
        for q in queries[:4]:  # Limit query execution to prevent rate limiting
            results = search_web(q, max_results=4)
            for r in results:
                search_results_compiled.append(
                    f"Title: {r['title']}\n"
                    f"URL: {r['url']}\n"
                    f"Snippet: {r['snippet']}\n"
                    f"---"
                )

        search_results_str = "\n".join(search_results_compiled)

        # Format prompt
        prompt = self.prompt_template.format(
            user_interests=user_interests,
            search_results=search_results_str
        )

        system_instruction = "You are a professional technology trend analyst and software architecture expert."

        # Call LLM
        try:
            candidates_list = self.llm_provider.generate_structured(
                prompt=prompt,
                response_model=TopicCandidatesList,
                system_instruction=system_instruction
            )
            if candidates_list and candidates_list.topics:
                return candidates_list.topics[:max_candidates]
        except Exception as e:
            print(f"Error: TopicAgent failed to synthesize candidates: {e}")

        # Fallback candidate generation if LLM or search returned no topics
        fallback_topics = []
        interests = [i.strip() for i in user_interests.split(",") if i.strip()] or [
            "Distributed Systems", "AI Engineering", "Cloud Native", "Database Internals"
        ]
        for idx, item in enumerate(interests):
            fallback_topics.append(
                TopicCandidate(
                    title=f"Modern {item} Architecture & Best Practices",
                    short_description=f"Key architectural designs, trade-offs, and scalability techniques in {item}.",
                    category=item,
                    trend_reason=f"High industry demand and rising 2026 adoption in {item}.",
                    evidence_sources=[],
                    estimated_interview_value=9,
                    trend_score=8
                )
            )
        return fallback_topics[:max_candidates]
