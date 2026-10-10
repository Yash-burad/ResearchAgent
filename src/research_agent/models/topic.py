from pydantic import BaseModel, Field
from typing import List, Dict

class TopicCandidate(BaseModel):
    title: str = Field(..., description="Name of the trending tech topic")
    short_description: str = Field(..., description="Brief summary of the topic")
    category: str = Field(..., description="Technology category (e.g., AI Infra, Backend, Distributed Systems)")
    trend_reason: str = Field(..., description="Why this topic is currently trending")
    evidence_sources: List[str] = Field(default_factory=list, description="List of source URLs showing evidence of trend")
    estimated_interview_value: int = Field(..., ge=1, le=10, description="Estimated score (1-10) for job interviews")
    trend_score: int = Field(..., ge=1, le=10, description="Current trend strength score (1-10)")

class RefinedTopic(BaseModel):
    title: str = Field(..., description="Name of the topic")
    reason_selected: str = Field(..., description="Detailed explanation of why this topic was selected")
    relevance_to_user: str = Field(..., description="How this topic aligns with the user's specific interests")
    expected_learning_outcome: str = Field(..., description="What the candidate will learn from studying this topic")
    scores: Dict[str, int] = Field(..., description="Breakdown of individual scores (interest_match, interview_value, etc.)")
    source_urls: List[str] = Field(default_factory=list, description="Scraped URLs to be used for deep research")
