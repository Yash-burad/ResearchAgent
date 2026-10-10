import pytest
from unittest.mock import patch
from research_agent.llm.mock_provider import MockProvider
from research_agent.models.stock import (
    StockProfile, FinancialAnalysis, ValuationAnalysis,
    PeerComparison, NewsAnalysis, EarningsAnalysis,
    CriticDebrief, StockResearchReport, StockOpportunityReport,
    StockCandidateOpportunity
)
from research_agent.agents.stock_entity_agent import StockEntityAgent
from research_agent.agents.stock_financial_agent import StockFinancialAgent
from research_agent.agents.stock_valuation_agent import StockValuationAgent
from research_agent.agents.stock_peer_agent import StockPeerAgent
from research_agent.agents.stock_news_agent import StockNewsAgent
from research_agent.agents.stock_earnings_agent import StockEarningsAgent
from research_agent.agents.stock_critic_agent import StockCriticAgent
from research_agent.agents.stock_synthesis_agent import StockSynthesisAgent
from research_agent.agents.stock_macro_agent import StockMacroAgent
from research_agent.agents.stock_dislocation_agent import StockDislocationAgent

@pytest.fixture
def mock_llm():
    return MockProvider()

@pytest.fixture
def sample_profile():
    return StockProfile(
        ticker="NVDA",
        company_name="NVIDIA Corporation",
        sector="Technology",
        industry="Semiconductors",
        current_price=120.0,
        market_cap_billions=2900.0,
        business_description="Global leader in accelerated computing.",
        monetization_engine="Compute & Networking, Graphics."
    )

def test_stock_entity_agent(mock_llm):
    agent = StockEntityAgent(mock_llm)
    profile = agent.resolve_entity("NVDA")
    assert isinstance(profile, StockProfile)
    assert profile.ticker == "NVDA"

def test_stock_financial_agent(mock_llm):
    agent = StockFinancialAgent(mock_llm)
    analysis = agent.analyze_financials("NVDA", "NVIDIA Corporation")
    assert isinstance(analysis, FinancialAnalysis)
    assert analysis.trajectory in ["Improving", "Stable", "Deteriorating"]
    assert len(analysis.revenue_trend_summary) > 0

def test_stock_valuation_agent(mock_llm):
    agent = StockValuationAgent(mock_llm)
    valuation = agent.analyze_valuation("NVDA", "NVIDIA Corporation", 120.0)
    assert isinstance(valuation, ValuationAnalysis)
    assert len(valuation.scenarios) > 0

def test_stock_peer_agent(mock_llm):
    agent = StockPeerAgent(mock_llm)
    peers = agent.analyze_peers("NVDA", "NVIDIA Corporation", "Technology", "Semiconductors")
    assert isinstance(peers, PeerComparison)
    assert len(peers.competitive_position_narrative) > 0
    assert len(peers.structural_moat_factors) >= 0

def test_stock_news_agent(mock_llm):
    with patch("research_agent.data.web_scraping_provider.WebScrapingProvider.search_stock_news", return_value=[
        {"title": "NVIDIA Blackwell Ramp", "url": "https://example.com/nvda", "snippet": "Demand strong", "source": "Reuters"}
    ]):
        agent = StockNewsAgent(mock_llm)
        news = agent.analyze_and_deduplicate_news("NVDA", "NVIDIA Corporation")
        assert isinstance(news, NewsAnalysis)
        assert len(news.recent_events) > 0

def test_stock_earnings_agent(mock_llm):
    agent = StockEarningsAgent(mock_llm)
    earnings = agent.analyze_earnings("NVDA", "NVIDIA Corporation")
    assert isinstance(earnings, EarningsAnalysis)
    assert len(earnings.quarterly_history) > 0

def test_stock_critic_agent(mock_llm):
    agent = StockCriticAgent(mock_llm)
    critic = agent.stress_test_thesis(
        ticker="NVDA",
        company_name="NVIDIA Corporation",
        sector="Technology",
        industry="Semiconductors",
        current_price=120.0,
        preliminary_synthesis={"thesis": "Leading AI hardware compute provider."}
    )
    assert isinstance(critic, CriticDebrief)
    assert len(critic.thesis_invalidation_triggers) > 0

def test_stock_synthesis_agent(mock_llm, sample_profile):
    financial_agent = StockFinancialAgent(mock_llm)
    valuation_agent = StockValuationAgent(mock_llm)
    peer_agent = StockPeerAgent(mock_llm)
    news_agent = StockNewsAgent(mock_llm)
    earnings_agent = StockEarningsAgent(mock_llm)
    critic_agent = StockCriticAgent(mock_llm)

    financials = financial_agent.analyze_financials("NVDA", "NVIDIA Corporation")
    valuation = valuation_agent.analyze_valuation("NVDA", "NVIDIA Corporation", 120.0)
    peers = peer_agent.analyze_peers("NVDA", "NVIDIA Corporation", "Technology", "Semiconductors")
    news = news_agent.analyze_and_deduplicate_news("NVDA", "NVIDIA Corporation")
    earnings = earnings_agent.analyze_earnings("NVDA", "NVIDIA Corporation")
    critic = critic_agent.stress_test_thesis("NVDA", "NVIDIA Corporation", "Technology", "Semiconductors", 120.0, {})

    synthesis_agent = StockSynthesisAgent(mock_llm)
    report = synthesis_agent.synthesize_report(
        profile=sample_profile,
        financials=financials,
        valuation=valuation,
        peers=peers,
        news=news,
        earnings=earnings,
        critic=critic
    )
    assert isinstance(report, StockResearchReport)
    assert report.ticker == "NVDA"
    assert len(report.valuation_scenarios) > 0
    assert len(report.historical_price_chart) > 0
    assert report.data_verification is not None
    assert report.data_verification.is_verified_latest is True

def test_data_freshness_verifier():
    from datetime import datetime
    from research_agent.data.verifier import DataFreshnessVerifier
    now_str = datetime.now().strftime("%Y-%m-%d")
    audit = DataFreshnessVerifier.verify(
        ticker="NVDA",
        current_price=124.50,
        historical_prices=[{"date": now_str, "close": 124.50, "volume": 50000000}]
    )
    assert audit.is_verified_latest is True
    assert audit.verified_as_of_date == now_str
    assert audit.latest_quote_date == now_str
    assert "PASSED" in audit.staleness_check

def test_stock_macro_agent(mock_llm):
    agent = StockMacroAgent(mock_llm)
    macro = agent.analyze_macro_and_sectors("Technology")
    assert "macro_summary" in macro
    assert "sector_trends" in macro

def test_stock_dislocation_agent(mock_llm):
    agent = StockDislocationAgent(mock_llm)
    opps = agent.screen_and_synthesize_opportunities({"macro_summary": "Stable", "sector_trends": {}}, "Technology")
    assert isinstance(opps, StockOpportunityReport)
    assert len(opps.candidates) > 0
