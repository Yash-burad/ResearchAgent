from pydantic import BaseModel, Field

class TopicSummary(BaseModel):
    topic: str = Field(..., description="The topic summarized")
    summary_markdown: str = Field(..., description="The full, compiled interview summary in markdown format")
