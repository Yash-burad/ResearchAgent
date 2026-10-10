import pytest
from fastapi.testclient import TestClient
from research_agent.web.app import app

@pytest.fixture
def client():
    return TestClient(app)

def test_get_home_feed(client):
    res = client.get("/api/feed")
    assert res.status_code == 200
    data = res.json()
    assert "hero_workout" in data
    assert "tech_radar" in data
    assert "stock_radar" in data
    assert "interview_radar" in data
    assert "total_bookmarks" in data

def test_bookmark_lifecycle(client):
    # Create bookmark
    payload = {
        "domain": "tech_topics",
        "item_type": "tech_summary",
        "title": "FastAPI Async Architecture",
        "reference_path": "outputs/run_test/summaries/fastapi.md",
        "summary": "Guide on Starlette event loops",
        "tags": ["#Python", "#FastAPI"],
        "metadata": {"reading_time_mins": 4}
    }
    create_res = client.post("/api/feed/bookmarks", json=payload)
    assert create_res.status_code == 200
    created = create_res.json()
    bm_id = created["id"]
    assert created["title"] == "FastAPI Async Architecture"

    # List bookmarks
    list_res = client.get("/api/feed/bookmarks?domain=tech_topics")
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(b["id"] == bm_id for b in items)

    # Delete bookmark
    del_res = client.delete(f"/api/feed/bookmarks/{bm_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "deleted"

def test_missed_questions_lifecycle(client):
    # Log missed question
    payload = {
        "title": "Sliding Window Maximum",
        "category": "DSA",
        "company": "Amazon",
        "what_tripped_me": "Forgot to maintain monotonic decreasing deque index invariant.",
        "difficulty": "Hard"
    }
    create_res = client.post("/api/feed/missed-questions", json=payload)
    assert create_res.status_code == 200
    created = create_res.json()
    q_id = created["id"]
    assert created["mastery_level"] == 0

    # Advance review
    update_res = client.put(f"/api/feed/missed-questions/{q_id}", json={
        "mastery_level": 1,
        "advance_review": True
    })
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["mastery_level"] == 1
    assert updated["review_count"] == 1

    # Clean up
    del_res = client.delete(f"/api/feed/missed-questions/{q_id}")
    assert del_res.status_code == 200

def test_telemetry_endpoint(client):
    payload = {
        "topic_slug": "distributed_transactions",
        "game_type": "flashcards",
        "result": "hesitated",
        "feedback_notes": "Took 35 seconds to answer 2PC coordinator failure mode"
    }
    res = client.post("/api/feed/telemetry", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["result"] == "hesitated"

def test_document_reader_safety(client):
    # Test reading existing file e.g. README.md
    res = client.get("/api/documents?path=README.md")
    assert res.status_code == 200
    assert res.json()["is_markdown"] is True
    assert "content" in res.json()

    # Test path traversal attack blocked
    res_traversal = client.get("/api/documents?path=../../../../etc/passwd")
    assert res_traversal.status_code in (403, 404)
