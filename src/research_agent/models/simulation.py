from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field
from datetime import datetime

class InterviewMessage(BaseModel):
    id: str = Field(..., description="Unique message ID")
    role: Literal["interviewer", "candidate", "system"] = Field(..., description="Sender role")
    content: str = Field(..., description="Message text or markdown content")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class InterviewSession(BaseModel):
    session_id: str
    run_id: str
    company_name: str
    role: str
    level: str
    round_name: str
    round_type: str
    evaluation_criteria: List[str] = Field(default_factory=list)
    messages: List[InterviewMessage] = Field(default_factory=list)
    status: Literal["in_progress", "completed"] = "in_progress"
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class RubricScore(BaseModel):
    criterion: str
    score: int = Field(..., ge=1, le=5, description="Score from 1 (Unsatisfactory) to 5 (Exceptional)")
    feedback: str

class InterviewFeedback(BaseModel):
    overall_score: int = Field(..., ge=0, le=100, description="Overall calibrated score out of 100")
    hire_recommendation: Literal["Strong Hire", "Hire", "Lean Hire", "Lean No Hire", "No Hire"]
    summary_verdict: str
    rubric_scores: List[RubricScore] = Field(default_factory=list)
    key_strengths: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)
    culture_fit_notes: str = ""
    detailed_debrief_markdown: str = ""

class StartSessionRequest(BaseModel):
    round_name: str
    round_type: Optional[str] = None

class SendMessageRequest(BaseModel):
    message: str

class HintRequest(BaseModel):
    context: Optional[str] = None
