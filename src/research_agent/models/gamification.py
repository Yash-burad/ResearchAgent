from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

GameType = Literal["flashcards", "quiz", "architecture_challenge"]

class FlashcardItem(BaseModel):
    id: str = Field(..., description="Unique ID for the flashcard within the deck")
    category: str = Field(..., description="Category tag (e.g. Core Architecture, Trade-offs, Scalability, Security)")
    difficulty: Literal["Easy", "Medium", "Hard"] = Field("Medium", description="Difficulty level")
    front_prompt: str = Field(..., description="The question, problem statement, or scenario prompt")
    back_explanation: str = Field(..., description="Detailed, concise technical explanation with clear reasoning")
    hint: Optional[str] = Field(None, description="Helpful hint guiding the candidate toward the answer")
    key_takeaway: Optional[str] = Field(None, description="One-sentence essential takeaway or interview soundbite")

class FlashcardsGame(BaseModel):
    topic: str
    game_type: Literal["flashcards"] = "flashcards"
    total_cards: int = 0
    cards: List[FlashcardItem] = Field(default_factory=list)

class TopicGameCollection(BaseModel):
    topic: str
    games: Dict[str, Any] = Field(default_factory=dict)
