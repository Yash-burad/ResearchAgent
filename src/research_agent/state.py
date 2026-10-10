from typing import TypedDict, List, Dict, Optional, Literal
from research_agent.models import (
    TopicCandidate, RefinedTopic, ResearchNotes, CompanyInterviewIntel,
    StockProfile, FinancialAnalysis, ValuationAnalysis, PeerComparison,
    NewsAnalysis, EarningsAnalysis, CriticDebrief, StockResearchReport,
    StockOpportunityReport
)

class ResearchAgentState(TypedDict):
    research_mode: Literal["tech_topics", "interview_experience", "stock_market"]
    user_interests: str
    target_audience: str
    
    # Company Interview Experience fields
    company_name: Optional[str]
    target_role: Optional[str]
    target_level: Optional[str]
    interview_intel: Optional[CompanyInterviewIntel]

    # Stock Market Intelligence fields
    stock_mode: Optional[Literal["stock_research", "stock_picks"]]
    stock_sub_mode: Optional[str]
    ticker: Optional[str]
    stock_ticker: Optional[str]
    stock_asset_class: Optional[str]
    stock_market_cap_tier: Optional[str]
    stock_investment_horizon: Optional[str]
    stock_risk_profile: Optional[str]
    manual_peers: Optional[List[str]]
    investment_horizon: Optional[str]
    sector_filter: Optional[str]
    stock_profile: Optional[StockProfile]
    stock_financials: Optional[FinancialAnalysis]
    stock_valuation: Optional[ValuationAnalysis]
    stock_peers: Optional[PeerComparison]
    stock_news: Optional[NewsAnalysis]
    stock_earnings: Optional[EarningsAnalysis]
    stock_critic: Optional[CriticDebrief]
    stock_research_report: Optional[StockResearchReport]
    stock_opportunity_report: Optional[StockOpportunityReport]

    # Tech Topics fields
    raw_topics: List[TopicCandidate]
    refined_topics: List[RefinedTopic]
    selected_topics: List[str]  # Titles of topics chosen for research
    research_notes: Dict[str, ResearchNotes]
    summaries: Dict[str, str]  # Topic Title -> Summary Markdown
    
    errors: List[str]
    run_id: str
    manual_selection: bool  # Toggle to trigger user interaction

