import tempfile
import pytest
from unittest.mock import patch
from research_agent.graph import create_research_graph
from research_agent.storage import RunStore
from research_agent.llm.mock_provider import MockProvider

def test_stock_research_graph_execution():
    with tempfile.TemporaryDirectory() as tmp_dir:
        with patch.object(RunStore, "DEFAULT_OUTPUTS_DIR", tmp_dir), \
             patch("research_agent.graph.get_llm_provider", return_value=MockProvider()), \
             patch("research_agent.data.web_scraping_provider.WebScrapingProvider.search_stock_news", return_value=[
                 {"title": "NVDA Earnings", "url": "http://example.com/nvda", "snippet": "Strong results", "source": "Bloomberg", "published_date": "2025-01-01"}
             ]):
            
            store = RunStore(outputs_dir=tmp_dir)
            run_id = store.create_run("test_stock_research_run")
            
            initial_state = {
                "research_mode": "stock_market",
                "stock_sub_mode": "stock_research",
                "stock_ticker": "NVDA",
                "stock_investment_horizon": "Long-Term Compounder (3-5 Years)",
                "stock_risk_profile": "Growth Oriented",
                "run_id": run_id,
                "errors": []
            }
            
            graph = create_research_graph()
            final_state = graph.invoke(initial_state)
            
            assert "stock_research_report" in final_state
            assert final_state["stock_research_report"] is not None
            assert final_state["stock_research_report"].ticker == "NVDA"
            assert len(final_state["stock_research_report"].valuation_scenarios) > 0
            
            # Verify output files exist
            assert (store.run_path / "stock_research_report.md").exists()
            assert (store.run_path / "stock_research_report.json").exists()

def test_stock_picks_graph_execution():
    with tempfile.TemporaryDirectory() as tmp_dir:
        with patch.object(RunStore, "DEFAULT_OUTPUTS_DIR", tmp_dir), \
             patch("research_agent.graph.get_llm_provider", return_value=MockProvider()):
            
            store = RunStore(outputs_dir=tmp_dir)
            run_id = store.create_run("test_stock_picks_run")
            
            initial_state = {
                "research_mode": "stock_market",
                "stock_sub_mode": "stock_picks",
                "stock_asset_class": "Equities",
                "stock_market_cap_tier": "Large Cap ($10B-$200B)",
                "run_id": run_id,
                "errors": []
            }
            
            graph = create_research_graph()
            final_state = graph.invoke(initial_state)
            
            assert "stock_opportunity_report" in final_state
            assert final_state["stock_opportunity_report"] is not None
            assert len(final_state["stock_opportunity_report"].candidates) > 0
            
            # Verify output files exist
            assert (store.run_path / "stock_opportunity_report.md").exists()
            assert (store.run_path / "stock_opportunity_report.json").exists()
