import pytest
from research_agent.data.valuation_engine import ValuationEngine
from research_agent.data.screener_engine import ScreenerEngine

def test_valuation_engine_cagr():
    cagr = ValuationEngine.calculate_cagr(100.0, 200.0, 3)
    assert cagr == pytest.approx(0.2599, abs=0.001)
    
    assert ValuationEngine.calculate_cagr(0.0, 100.0, 3) == 0.0
    assert ValuationEngine.calculate_cagr(100.0, 200.0, 0) == 0.0

def test_valuation_engine_dcf():
    scenarios = ValuationEngine.calculate_dcf_scenarios(
        current_price=100.0,
        latest_revenue_millions=50000.0,
        shares_outstanding_millions=2500.0
    )
    assert len(scenarios) == 3
    names = [s.scenario_name for s in scenarios]
    assert "Bear" in names
    assert "Base" in names
    assert "Bull" in names
    
    base = next(s for s in scenarios if s.scenario_name == "Base")
    assert base.target_price_implied > 0
    assert len(base.key_assumptions) > 0

def test_screener_engine():
    candidates = ScreenerEngine.screen_opportunities(
        sector_filter="Technology",
        candidates_limit=3
    )
    assert len(candidates) >= 1
    for c in candidates:
        assert c.current_price > 0
        assert c.implied_upside_percent != 0.0
        assert c.opportunity_archetype in [
            "Quality Growth + Temporary Selloff",
            "Improving Fundamentals + Multiple Compression",
            "Earnings Inflection + Unrecognized Catalyst",
            "Capital Allocation & FCF Inflection"
        ]
