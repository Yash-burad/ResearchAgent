import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from research_agent.models import (
    InterviewRound,
    CompanyInterviewIntel,
    ResearchSource
)
from research_agent.llm.mock_provider import MockProvider
from research_agent.agents.interview_intel_agent import InterviewIntelAgent
from research_agent.storage import RunStore
from research_agent.graph import create_research_graph
from research_agent.web.app import app
from research_agent.storage.run_tracker import RUNS_DB

client = TestClient(app)

def test_company_interview_intel_model():
    intel = CompanyInterviewIntel(
        company_name="Stripe",
        role="Staff Backend Engineer",
        level="Staff / L6",
        hiring_bar_summary="Comprehensive hiring bar for Stripe staff engineering.",
        rounds_breakdown=[
            InterviewRound(
                round_name="Bug Bash / Code Integration",
                round_type="Practical / Bug Squash / API",
                duration_minutes=60,
                focus_areas=["Debugging unfamiliar open source codebase", "Writing unit tests"],
                sample_questions=["Fix race condition in billing scheduler"],
                evaluation_criteria=["Speed of navigation", "Clean fixes", "Test coverage"],
                tips=["Run existing test suite immediately"]
            )
        ],
        top_dsa_patterns=["Rate Limiter implementation", "LRU Cache with expiration"],
        top_system_design_topics=["Idempotent payment ledger", "Webhook delivery platform"],
        cultural_values_and_behavioral=["Macro and micro craft", "High agency", "First-principles thinking"],
        recent_experiences_summary=["Heavy practical craft focus in local IDE", "Idempotency depth"],
        sources=[
            ResearchSource(
                url="https://leetcode.com/discuss",
                title="Stripe Staff Interview Experience",
                publisher="LeetCode Discuss",
                extracted_at="2026-09-18 12:00:00",
                credibility_score=9,
                key_points=["Practical debugging round"]
            )
        ],
        prep_pack_markdown="# Stripe Staff Engineer Interview Pack\n..."
    )

    assert intel.company_name == "Stripe"
    assert intel.role == "Staff Backend Engineer"
    assert len(intel.rounds_breakdown) == 1
    assert intel.top_dsa_patterns[0] == "Rate Limiter implementation"

def test_interview_intel_agent_with_mock():
    mock_llm = MockProvider()
    agent = InterviewIntelAgent(mock_llm)

    intel = agent.research_company(
        company_name="Stripe",
        role="Staff Backend Engineer",
        level="Staff / L6"
    )

    assert isinstance(intel, CompanyInterviewIntel)
    assert intel.company_name == "Stripe"
    assert intel.role == "Staff Backend Engineer"
    assert len(intel.rounds_breakdown) > 0
    assert "Stripe" in intel.prep_pack_markdown

def test_run_store_save_and_load_interview_intel():
    store = RunStore()
    run_id = store.create_run()

    intel = CompanyInterviewIntel(
        company_name="Google",
        role="Staff Systems Engineer",
        level="L6",
        hiring_bar_summary="Google L6 systems bar test.",
        rounds_breakdown=[],
        top_dsa_patterns=["Trie", "Topological Sort"],
        top_system_design_topics=["Global Spanner replication"],
        cultural_values_and_behavioral=["Googleyness", "Navigating Ambiguity"],
        recent_experiences_summary=["Large scale distributed systems and strong DSA fundamentals."],
        sources=[],
        prep_pack_markdown="# Google L6 Pack\nIntel details."
    )

    store.save_interview_intel(intel)
    assert (store.run_path / "interview_intel.json").exists()
    assert (store.run_path / "company_interview_pack.md").exists()

    loaded = store.load_interview_intel()
    assert loaded is not None
    assert loaded["company_name"] == "Google"
    assert loaded["top_dsa_patterns"] == ["Trie", "Topological Sort"]


def test_graph_interview_experience_flow():
    with patch("research_agent.graph.get_llm_provider", return_value=MockProvider()):
        graph = create_research_graph()
        
        state = {
            "research_mode": "interview_experience",
            "company_name": "Stripe",
            "target_role": "Staff Backend Engineer",
            "target_level": "Staff / L6",
            "user_interests": "",
            "target_audience": "Staff",
            "raw_topics": [],
            "refined_topics": [],
            "selected_topics": [],
            "research_notes": {},
            "summaries": {},
            "errors": [],
            "run_id": "test_graph_interview_run",
            "manual_selection": False
        }

        output = graph.invoke(state)
        assert "interview_intel" in output
        assert output["interview_intel"].company_name == "Stripe"

def test_web_api_interview_experience():
    with patch("research_agent.web.app.run_graph_in_background") as mock_bg:
        response = client.post("/api/runs", json={
            "mode": "interview_experience",
            "company_name": "Databricks",
            "target_role": "Principal Systems Engineer",
            "target_level": "Principal / L7",
            "manual_selection": False
        })
        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data
        run_id = data["run_id"]
        assert run_id in RUNS_DB
        assert RUNS_DB[run_id]["company_name"] == "Databricks"
        assert RUNS_DB[run_id]["target_role"] == "Principal Systems Engineer"

def test_get_interview_intel_endpoint():
    run_id = "test_run_intel_api"
    mock_intel = CompanyInterviewIntel(
        company_name="Netflix",
        role="Senior Platform Engineer",
        level="Senior / L5",
        hiring_bar_summary="Netflix distributed systems testing.",
        rounds_breakdown=[],
        top_dsa_patterns=[],
        top_system_design_topics=["Chaos Engineering Platform"],
        cultural_values_and_behavioral=["Freedom and Responsibility"],
        recent_experiences_summary=["Emphasis on high alignment and loose coupling."],
        sources=[],
        prep_pack_markdown="# Netflix Intel Pack"
    )

    RUNS_DB[run_id] = {
        "status": "completed",
        "progress": 100,
        "current_step": "Complete",
        "interests": "",
        "company_name": "Netflix",
        "target_role": "Senior Platform Engineer",
        "target_level": "Senior / L5",
        "raw_topics": [],
        "refined_topics": [],
        "selected_topics": ["Netflix (Senior Platform Engineer)"],
        "final_pack": "# Netflix Intel Pack",
        "interview_intel": mock_intel.model_dump(),
        "error": None
    }

    res = client.get(f"/api/runs/{run_id}/interview-intel")
    assert res.status_code == 200
    assert res.json()["company_name"] == "Netflix"
    assert res.json()["top_system_design_topics"] == ["Chaos Engineering Platform"]
