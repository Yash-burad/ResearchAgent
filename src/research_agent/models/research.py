from pydantic import BaseModel, Field
from typing import List, Optional

class ResearchSource(BaseModel):
    url: str = Field(..., description="URL of the source website or paper")
    title: str = Field(..., description="Title of the page/article")
    publisher: Optional[str] = Field(None, description="Publisher name (e.g., TechCrunch, AWS Blog)")
    extracted_at: str = Field(..., description="Timestamp of retrieval")
    credibility_score: int = Field(..., ge=1, le=10, description="Assessed reliability score of source")
    key_points: List[str] = Field(default_factory=list, description="Primary facts extracted from this source")

class ResearchNotes(BaseModel):
    topic: str = Field(..., description="Topic being researched")
    definition: str = Field(..., description="Formal definition or explanation of the concept")
    why_it_matters: List[str] = Field(default_factory=list, description="Points explaining why this technology is important")
    technical_details: List[str] = Field(default_factory=list, description="Under the hood/architectural details")
    examples: List[str] = Field(default_factory=list, description="Code or concrete scenario examples")
    use_cases: List[str] = Field(default_factory=list, description="Real-world industrial use cases")
    limitations: List[str] = Field(default_factory=list, description="Drawbacks, performance issues, or architectural limitations")
    related_topics: List[str] = Field(default_factory=list, description="Related terms or concepts for further study")
    sources: List[ResearchSource] = Field(default_factory=list, description="List of source materials used to compile notes")
