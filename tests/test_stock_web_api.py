import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from research_agent.web.app import app
from research_agent.storage.run_tracker import RUNS_DB
from research_agent.models.stock import (
    StockProfile, ValuationScenario, CriticDebrief,
    StockResearchReport, StockCandidateOpportunity,
    StockOpportunityReport
)

client = TestClient(app)

def test_create_stock_research_run():
    with patch("research_agent.web.app.run_graph_in_background") as mock_bg:
        response = client.post("/api/runs", json={
            "research_mode": "stock_market",
            "stock_sub_mode": "stock_research",
            "stock_ticker": "NVDA",
            "stock_investment_horizon": "Long-Term Compounder (3-5 Years)",
            "stock_risk_profile": "Growth Oriented"
        })
        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data
        run_id = data["run_id"]
        assert run_id in RUNS_DB
        assert RUNS_DB[run_id]["research_mode"] == "stock_market"
        assert RUNS_DB[run_id]["stock_sub_mode"] == "stock_research"
        assert RUNS_DB[run_id]["stock_ticker"] == "NVDA"

def test_create_stock_picks_run():
    with patch("research_agent.web.app.run_graph_in_background") as mock_bg:
        response = client.post("/api/runs", json={
            "research_mode": "stock_market",
            "stock_sub_mode": "stock_picks",
            "stock_asset_class": "Equities",
            "stock_market_cap_tier": "Large Cap ($10B-$200B)"
        })
        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data
        run_id = data["run_id"]
        assert run_id in RUNS_DB
        assert RUNS_DB[run_id]["stock_sub_mode"] == "stock_picks"
        assert RUNS_DB[run_id]["stock_asset_class"] == "Equities"

def test_get_stock_research_result():
    run_id = "test_stock_res_123"
    critic = CriticDebrief(
        overlooked_risks=["Concentration"],
        contradictory_data_points=["ASIC chips"],
        bull_case_flaws=["CapEx peak"],
        thesis_invalidation_triggers=["Deceleration < 10%"],
        confidence_penalty_points=5
    )
    report = StockResearchReport(
        ticker="NVDA",
        company_name="NVIDIA Corp",
        sector="Technology",
        industry="Semiconductors",
        current_price=120.0,
        market_cap_billions=2900.0,
        executive_summary="Dominant accelerated computing platform.",
        business_model_and_revenue_engines="Compute & Networking, Graphics.",
        financial_health_and_margin_trends="75% gross margins, high ROIC.",
        valuation_analysis="Attractive on PEG basis.",
        peer_comparison_narrative="Wide moat vs competitors.",
        management_capital_allocation_scorecard="Superb capital return and R&D reinvestment.",
        competitive_moat_analysis="CUDA software ecosystem moat.",
        what_could_invalidate_the_thesis="Cloud CapEx pause.",
        why_now="Blackwell cycle inflection.",
        critic_debrief=critic,
        report_markdown="# NVDA Deep-Dive Report"
    )
    
    RUNS_DB[run_id] = {
        "status": "completed",
        "progress": 100,
        "research_mode": "stock_market",
        "stock_sub_mode": "stock_research",
        "stock_research_report": report.model_dump(),
        "error": None
    }
    
    res = client.get(f"/api/runs/{run_id}/stock-research")
    assert res.status_code == 200
    data = res.json()
    assert data["ticker"] == "NVDA"
    assert data["current_price"] == 120.0

def test_get_stock_picks_result():
    run_id = "test_stock_picks_123"
    cand = StockCandidateOpportunity(
        ticker="NVDA",
        company_name="NVIDIA Corp",
        sector="Technology",
        current_price=120.0,
        opportunity_archetype="Quality Growth + Temporary Selloff",
        why_now="Pullback before earnings",
        fundamental_highlights=["High ROIC"],
        catalysts=["Blackwell ramp"],
        critical_risks=["CapEx digestion"],
        implied_upside_percent=25.0,
        confidence_tier="High Conviction"
    )
    report = StockOpportunityReport(
        macro_context_summary="Favorable tech capex environment.",
        sector_tailwinds_and_headwinds={"Tech": "AI tailwinds"},
        screener_criteria_applied={"ROIC": ">15%"},
        candidates=[cand],
        critic_risk_summary="Macro rate duration risk",
        report_markdown="# Stock Picks Report"
    )
    
    RUNS_DB[run_id] = {
        "status": "completed",
        "progress": 100,
        "research_mode": "stock_market",
        "stock_sub_mode": "stock_picks",
        "stock_opportunity_report": report.model_dump(),
        "error": None
    }
    
    res = client.get(f"/api/runs/{run_id}/stock-picks")
    assert res.status_code == 200
    data = res.json()
    assert len(data["candidates"]) == 1
    assert data["candidates"][0]["ticker"] == "NVDA"
