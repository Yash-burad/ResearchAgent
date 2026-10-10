import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from research_agent.web.app import app
from research_agent.storage.run_tracker import RUNS_DB
from research_agent.llm.mock_provider import MockProvider

client = TestClient(app)

def test_static_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text

def test_create_run_api():
    with patch("research_agent.web.app.run_graph_in_background") as mock_bg:
        response = client.post("/api/runs", json={
            "interests": "distributed systems, databases",
            "manual_selection": False
        })
        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data
        run_id = data["run_id"]
        assert run_id in RUNS_DB
        assert RUNS_DB[run_id]["status"] == "discovering"

def test_get_run_status_and_topics():
    run_id = "test_run_123"
    RUNS_DB[run_id] = {
        "status": "pending_selection",
        "progress": 50,
        "current_step": "Awaiting topic selection",
        "interests": "cloud infrastructure",
        "raw_topics": [{"title": "Serverless V8", "short_description": "desc", "category": "Cloud", "trend_reason": "r", "evidence_sources": [], "estimated_interview_value": 8, "trend_score": 8}],
        "refined_topics": [{"title": "Serverless V8", "reason_selected": "s", "relevance_to_user": "u", "expected_learning_outcome": "l", "scores": {}, "source_urls": []}],
        "selected_topics": [],
        "final_pack": "# Final Pack Content",
        "error": None
    }
    
    # Check status
    res = client.get(f"/api/runs/{run_id}")
    assert res.status_code == 200
    assert res.json()["status"] == "pending_selection"
    
    # Check topics
    res_topics = client.get(f"/api/runs/{run_id}/topics")
    assert res_topics.status_code == 200
    assert len(res_topics.json()["refined_topics"]) == 1
    
    # Check final pack
    res_pack = client.get(f"/api/runs/{run_id}/final-pack")
    assert res_pack.status_code == 200
    assert "# Final Pack Content" in res_pack.json()["final_pack"]

def test_select_topics_endpoint():
    run_id = "test_run_select"
    RUNS_DB[run_id] = {
        "status": "pending_selection",
        "progress": 50,
        "current_step": "Awaiting topic selection",
        "interests": "cloud infrastructure",
        "raw_topics": [{"title": "Serverless V8", "short_description": "desc", "category": "Cloud", "trend_reason": "r", "evidence_sources": [], "estimated_interview_value": 8, "trend_score": 8}],
        "refined_topics": [{"title": "Serverless V8", "reason_selected": "s", "relevance_to_user": "u", "expected_learning_outcome": "l", "scores": {}, "source_urls": []}],
        "selected_topics": [],
        "final_pack": "",
        "error": None
    }
    
    with patch("research_agent.web.app.run_graph_in_background"):
        res = client.post(f"/api/runs/{run_id}/select-topics", json={
            "selected_topics": ["Serverless V8"]
        })
        assert res.status_code == 200
        assert res.json()["status"] == "resumed"
        assert RUNS_DB[run_id]["status"] == "researching"
        assert RUNS_DB[run_id]["selected_topics"] == ["Serverless V8"]
