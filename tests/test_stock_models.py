import pytest
from research_agent.models.stock import (
    SourceClaim, StockProfile, FinancialStatementSummary,
    FinancialAnalysis, ValuationScenario, ValuationAnalysis,
    PeerBenchmark, PeerComparison, NewsEvent, NewsAnalysis,
    EarningsTrackRecord, EarningsAnalysis, CriticDebrief,
    StockResearchReport, StockCandidateOpportunity, StockOpportunityReport
)

def test_source_claim_model():
    claim = SourceClaim(
        claim_text="Gross margin expanded to 75% in FY2025.",
        claim_type="FACT",
        source_title="SEC Form 10-K",
        source_url="https://www.sec.gov/edgar"
    )
    assert claim.claim_type == "FACT"
    assert claim.confidence_score == 1.0

def test_valuation_scenario_model():
    scenario = ValuationScenario(
        scenario_name="Base",
        target_price_implied=145.0,
        upside_downside_percent=16.5,
        revenue_growth_cagr=28.0,
        terminal_operating_margin=58.0,
        wacc=9.5,
        terminal_growth_rate=3.0,
        implied_pe_multiple=30.0,
        key_assumptions=["Volume ramp on schedule"],
        catalysts_required=["Cloud buildouts"],
        risks_to_scenario=["TSMC capacity"]
    )
    assert scenario.scenario_name == "Base"
    assert scenario.target_price_implied == 145.0

def test_critic_debrief_model():
    critic = CriticDebrief(
        overlooked_risks=["Customer concentration"],
        contradictory_data_points=["Custom ASIC buildouts"],
        bull_case_flaws=["Assumes non-cyclical CapEx"],
        thesis_invalidation_triggers=["Sequential revenue deceleration below 5% QoQ"],
        confidence_penalty_points=5
    )
    assert len(critic.thesis_invalidation_triggers) == 1
    assert critic.confidence_penalty_points == 5

def test_stock_candidate_opportunity_model():
    cand = StockCandidateOpportunity(
        ticker="NVDA",
        company_name="NVIDIA Corp",
        sector="Technology",
        current_price=124.50,
        opportunity_archetype="Quality Growth + Temporary Selloff",
        why_now="8% pullback prior to product cycle inflection.",
        fundamental_highlights=["65% ROIC"],
        catalysts=["Volume ramp"],
        critical_risks=["Customer concentration"],
        implied_upside_percent=32.0,
        confidence_tier="High Conviction"
    )
    assert cand.opportunity_archetype == "Quality Growth + Temporary Selloff"
    assert cand.confidence_tier == "High Conviction"

def test_data_verification_audit_model():
    from research_agent.models.stock import DataVerificationAudit
    from datetime import datetime
    now_str = datetime.now().strftime("%Y-%m-%d")
    audit = DataVerificationAudit(
        is_verified_latest=True,
        verified_as_of_date=now_str,
        verification_status="VERIFIED_LATEST",
        latest_quote_date=now_str,
        staleness_check="PASSED: Market Current (0-day lag)",
        verification_source="Live Exchange Feed & SEC EDGAR",
        audit_notes="Data verified current."
    )
    assert audit.is_verified_latest is True
    assert audit.verification_status == "VERIFIED_LATEST"
    assert audit.verified_as_of_date == now_str

def test_stock_report_verification_and_chart():
    from datetime import datetime
    critic = CriticDebrief(overlooked_risks=["Test Risk"])
    report = StockResearchReport(
        ticker="NVDA",
        company_name="NVIDIA Corporation",
        sector="Technology",
        industry="Semiconductors",
        current_price=124.50,
        market_cap_billions=3060.0,
        executive_summary="**30-Second Verdict**: Leading AI compute compounder.",
        business_model_and_revenue_engines="- **What They Sell**: GPUs and CUDA.",
        financial_health_and_margin_trends="- **Are they making money?**: Yes, 62% operating margin.",
        valuation_analysis="Attractive on PEG.",
        peer_comparison_narrative="Wide moat.",
        management_capital_allocation_scorecard="Balanced.",
        competitive_moat_analysis="CUDA software moat.",
        what_could_invalidate_the_thesis="Cloud CapEx freeze.",
        why_now="Blackwell cycle.",
        critic_debrief=critic,
        historical_price_chart=[{"date": "2026-09-26", "close": 124.50, "volume": 50000000}]
    )
    assert report.ticker == "NVDA"
    assert len(report.historical_price_chart) == 1
    assert report.data_verification is not None
    assert report.data_verification.is_verified_latest is True
    assert report.verified_as_of_date == datetime.now().strftime("%Y-%m-%d")
