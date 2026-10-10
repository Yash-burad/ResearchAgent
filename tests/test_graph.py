import tempfile
import pytest
from unittest.mock import patch
from research_agent.graph import create_research_graph
from research_agent.storage import RunStore
from research_agent.storage.run_tracker import RUNS_DB
from research_agent.llm.mock_provider import MockProvider

def test_full_graph_automated_execution():
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Patch outputs_dir to temporary test folder
        with patch.object(RunStore, "DEFAULT_OUTPUTS_DIR", tmp_dir), \
             patch("research_agent.graph.get_llm_provider", return_value=MockProvider()), \
             patch("research_agent.agents.topic_agent.search_web", return_value=[{"title": "T", "url": "http://x", "snippet": "S"}]), \
             patch("research_agent.agents.researcher_agent.search_web", return_value=[{"title": "T", "url": "http://x", "snippet": "S"}]), \
             patch("research_agent.agents.researcher_agent.scrape_url", return_value="Scraped test content"):
            
            store = RunStore(outputs_dir=tmp_dir)
            run_id = store.create_run("test_graph_run")
            
            initial_state = {
                "user_interests": "AI Infrastructure, Distributed Systems",
                "target_audience": "Mid-Senior Level",
                "raw_topics": [],
                "refined_topics": [],
                "selected_topics": [],
                "research_notes": {},
                "summaries": {},
                "errors": [],
                "run_id": run_id,
                "manual_selection": False
            }
            
            graph = create_research_graph()
            final_state = graph.invoke(initial_state)
            
            assert "raw_topics" in final_state
            assert len(final_state["raw_topics"]) > 0
            assert "refined_topics" in final_state
            assert len(final_state["refined_topics"]) > 0
            assert "summaries" in final_state
            assert len(final_state["summaries"]) > 0
            
            # Verify output files exist
            assert (store.run_path / "trending_topics.md").exists()
            assert (store.run_path / "refined_topics.md").exists()
            assert (store.run_path / "final_interview_pack.md").exists()

def test_graph_manual_selection_early_exit():
    with tempfile.TemporaryDirectory() as tmp_dir:
        with patch.object(RunStore, "DEFAULT_OUTPUTS_DIR", tmp_dir), \
             patch("research_agent.graph.get_llm_provider", return_value=MockProvider()), \
             patch("research_agent.agents.topic_agent.search_web", return_value=[]):
            
            store = RunStore(outputs_dir=tmp_dir)
            run_id = store.create_run("test_manual_run")
            
            initial_state = {
                "user_interests": "AI Infrastructure",
                "target_audience": "Mid-Senior Level",
                "raw_topics": [],
                "refined_topics": [],
                "selected_topics": [],
                "research_notes": {},
                "summaries": {},
                "errors": [],
                "run_id": run_id,
                "manual_selection": True
            }
            
            graph = create_research_graph()
            state_after_refinement = graph.invoke(initial_state)
            
            # Should pause before researching because manual_selection is True and selected_topics is empty
            assert len(state_after_refinement["refined_topics"]) > 0
            assert len(state_after_refinement["summaries"]) == 0
            assert RUNS_DB.get(run_id, {}).get("status") == "pending_selection"
