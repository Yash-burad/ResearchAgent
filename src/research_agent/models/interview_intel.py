from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from research_agent.models.research import ResearchSource

RoundType = Literal["Coding / DSA", "System Design", "Behavioral & Leadership", "Hiring Manager", "Practical / Bug Squash / API", "Domain Deep-Dive"]

class InterviewRound(BaseModel):
    round_name: str = Field(..., description="Name/title of the round (e.g., Round 1: Coding & Data Structures)")
    round_type: str = Field("Coding / DSA", description="Category of the round")
    duration_minutes: int = Field(45, description="Expected duration in minutes")
    focus_areas: List[str] = Field(default_factory=list, description="Primary technical skills or themes assessed")
    sample_questions: List[str] = Field(default_factory=list, description="Representative questions asked in this round")
    evaluation_criteria: List[str] = Field(default_factory=list, description="What interviewers look for (signals for a 'Strong Hire')")
    tips: List[str] = Field(default_factory=list, description="Candidate advice & strategy for this specific round")

class InterviewQuestionItem(BaseModel):
    question_text: str = Field(..., description="The interview question or problem prompt")
    category: str = Field(..., description="Category (e.g. Dynamic Programming, Distributed Caching, Conflict Resolution)")
    difficulty: Literal["Easy", "Medium", "Hard"] = Field("Medium", description="Difficulty rating")
    frequency_rating: str = Field("High", description="How frequently this pattern is reported (Very High, High, Medium)")
    approach_guide: str = Field(..., description="Recommended technical approach and solution blueprint")
    common_pitfalls: List[str] = Field(default_factory=list, description="Common mistakes candidates make")

class CompanyInterviewIntel(BaseModel):
    company_name: str
    role: str
    level: str
    hiring_bar_summary: str = Field(..., description="Overview of the company's hiring philosophy, difficulty, and standard bar")
    rounds_breakdown: List[InterviewRound] = Field(default_factory=list)
    top_dsa_patterns: List[str] = Field(default_factory=list, description="Most frequent DSA algorithms and patterns asked")
    top_system_design_topics: List[str] = Field(default_factory=list, description="Frequent system design problems and architectures")
    cultural_values_and_behavioral: List[str] = Field(default_factory=list, description="Company values, leadership principles, or behavioral themes")
    recent_experiences_summary: List[str] = Field(default_factory=list, description="Key takeaways from recent 2025/2026 candidate debriefs")
    sources: List[ResearchSource] = Field(default_factory=list)
    prep_pack_markdown: str = Field("", description="Full compiled Markdown interview prep document")
