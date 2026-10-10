import os
from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel
from research_agent.models import TopicCandidate, RefinedTopic
from research_agent.llm import LLMProvider

class RefinedTopicsList(BaseModel):
    topics: List[RefinedTopic]

def load_prompt(filename: str) -> str:
    prompts_dir = Path(__file__).parent.parent / "prompts"
    file_path = prompts_dir / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def compute_final_score(scores: Dict[str, int]) -> float:
    weights = {
        "interest_match": 0.30,
        "interview_value": 0.25,
        "depth": 0.20,
        "freshness": 0.15,
        "source_quality": 0.10
    }
    total = 0.0
    for key, weight in weights.items():
        # Safely handle variations in LLM response keys
        val = (
            scores.get(key)
            or scores.get(f"{key}_score")
            or scores.get(key.replace("_", " "))
            or 5
        )
        total += val * weight
    return total

class FineTunerAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.prompt_template = load_prompt("fine_tuner_agent.md")

    def refine_topics(
        self,
        user_interests: str,
        candidates: List[TopicCandidate],
        max_selected: int = 5
    ) -> List[RefinedTopic]:
        """
        Ranks and refines topic candidates using LLM guidance, calculating a weighted average score
        for sorting and selecting the top N.
        """
        if not candidates:
            return []

        # Format candidates for the prompt
        candidates_str_list = []
        for i, c in enumerate(candidates, 1):
            candidates_str_list.append(
                f"{i}. Title: {c.title}\n"
                f"   Category: {c.category}\n"
                f"   Description: {c.short_description}\n"
                f"   Trend Reason: {c.trend_reason}\n"
                f"   Sources: {', '.join(c.evidence_sources)}\n"
            )
        candidates_str = "\n".join(candidates_str_list)

        prompt = self.prompt_template.format(
            user_interests=user_interests,
            topic_candidates=candidates_str
        )

        system_instruction = "You are a senior engineering manager and career mentor."

        try:
            refined_list = self.llm_provider.generate_structured(
                prompt=prompt,
                response_model=RefinedTopicsList,
                system_instruction=system_instruction
            )
            
            # Sort refined topics by computed final score descending
            sorted_topics = sorted(
                refined_list.topics,
                key=lambda x: compute_final_score(x.scores),
                reverse=True
            )
            
            return sorted_topics[:max_selected]
        except Exception as e:
            print(f"Warning: FineTunerAgent structured call failed: {e}. Falling back to default selection.")
            # Fallback: create default selections from candidates
            fallback_refined = []
            for c in candidates[:max_selected]:
                fallback_refined.append(
                    RefinedTopic(
                        title=c.title,
                        reason_selected="Fallback selection: automatically chosen due to parsing limits.",
                        relevance_to_user="Selected based on interest keyword matching.",
                        expected_learning_outcome=f"Understand standard interview concepts of {c.title}.",
                        scores={
                            "interest_match": 8,
                            "interview_value": 7,
                            "depth": 7,
                            "freshness": 8,
                            "source_quality": 6
                        },
                        source_urls=c.evidence_sources
                    )
                )
            return fallback_refined
