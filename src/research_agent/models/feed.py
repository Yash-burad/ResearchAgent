from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# Domain Literals
FeedDomain = Literal["tech_topics", "stock_market", "interview_experience"]
BookmarkItemType = Literal["tech_summary", "stock_research", "stock_pick", "interview_guide", "external_article"]
QuestionCategory = Literal["DSA", "System Design", "Practical Bug Squashing", "Behavioral", "Core CS"]
QuestionDifficulty = Literal["Easy", "Medium", "Hard"]
TelemetryResult = Literal["easy", "hesitated", "stumbled", "hint_used"]

# ----------------- Bookmarks -----------------

class BookmarkItem(BaseModel):
    id: int
    domain: FeedDomain
    item_type: BookmarkItemType
    title: str
    summary: str = ""
    reference_path: str
    external_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str

class CreateBookmarkRequest(BaseModel):
    domain: FeedDomain
    item_type: BookmarkItemType
    title: str
    reference_path: str
    summary: Optional[str] = ""
    external_url: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

# ----------------- Missed Questions (Stumble Log) -----------------

class MissedQuestionItem(BaseModel):
    id: int
    title: str
    category: QuestionCategory
    company: Optional[str] = None
    what_tripped_me: str
    source: Literal["manual_entry", "mock_interview", "flashcard_game"] = "manual_entry"
    difficulty: QuestionDifficulty = "Medium"
    mastery_level: int = 0  # 0: Stumbled, 1: Reviewed, 2: Mastered
    review_count: int = 0
    next_review_due: Optional[str] = None
    created_at: str
    updated_at: str

class CreateMissedQuestionRequest(BaseModel):
    title: str
    category: QuestionCategory = "DSA"
    company: Optional[str] = None
    what_tripped_me: str
    source: Literal["manual_entry", "mock_interview", "flashcard_game"] = "manual_entry"
    difficulty: QuestionDifficulty = "Medium"

class UpdateMissedQuestionRequest(BaseModel):
    mastery_level: Optional[int] = None
    what_tripped_me: Optional[str] = None
    advance_review: Optional[bool] = None

# ----------------- Telemetry -----------------

class LearningTelemetryItem(BaseModel):
    id: int
    topic_slug: str
    card_id: Optional[str] = None
    game_type: str = "flashcards"
    result: TelemetryResult
    feedback_notes: Optional[str] = None
    created_at: str

class LogTelemetryRequest(BaseModel):
    topic_slug: str
    card_id: Optional[str] = None
    game_type: str = "flashcards"
    result: TelemetryResult
    feedback_notes: Optional[str] = None

# ----------------- Aggregated Feed Models -----------------

class RecentSearchItem(BaseModel):
    query_text: str
    domain: str
    count: int
    score: float
    last_searched: str
    run_id: Optional[str] = None

class StockWatchlistItem(BaseModel):
    ticker: str
    company_name: str
    current_price: Optional[float] = None
    dcf_target_price: Optional[float] = None
    dcf_upside_percent: Optional[float] = None
    conviction: str = "Neutral"
    critic_warning: Optional[str] = None
    run_id: Optional[str] = None
    last_updated: str

class HeroWorkout(BaseModel):
    total_due: int
    due_questions: List[MissedQuestionItem] = Field(default_factory=list)
    suggested_focus: Optional[str] = None

class TechRadarSection(BaseModel):
    trending_topics: List[RecentSearchItem] = Field(default_factory=list)
    saved_articles: List[BookmarkItem] = Field(default_factory=list)

class StockRadarSection(BaseModel):
    watchlist: List[StockWatchlistItem] = Field(default_factory=list)
    saved_reports: List[BookmarkItem] = Field(default_factory=list)
    recent_picks: List[Dict[str, Any]] = Field(default_factory=list)
    peer_recommendations: List[Dict[str, Any]] = Field(default_factory=list)

class InterviewRadarSection(BaseModel):
    recent_company_guides: List[Dict[str, Any]] = Field(default_factory=list)
    missed_questions: List[MissedQuestionItem] = Field(default_factory=list)
    recent_mock_sessions: List[Dict[str, Any]] = Field(default_factory=list)

class HomeFeedResponse(BaseModel):
    hero_workout: HeroWorkout
    tech_radar: TechRadarSection
    stock_radar: StockRadarSection
    interview_radar: InterviewRadarSection
    total_bookmarks: int = 0
