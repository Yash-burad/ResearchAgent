import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta

from research_agent.storage.feed_store import FeedStore
from research_agent.services.feed_service import FeedService
from research_agent.models.feed import (
    CreateBookmarkRequest,
    CreateMissedQuestionRequest,
    UpdateMissedQuestionRequest,
    LogTelemetryRequest
)

@pytest.fixture
def temp_feed_store():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_user_profile.db"
        store = FeedStore(db_path=str(db_path))
        yield store

def test_feed_store_initialization(temp_feed_store):
    assert temp_feed_store.db_path.exists()
    assert temp_feed_store.list_bookmarks() == []
    assert temp_feed_store.list_missed_questions() == []

def test_activity_logging_and_trends(temp_feed_store):
    # Log several activities
    temp_feed_store.log_activity("tech_topics", "Vector DB", "run_1")
    temp_feed_store.log_activity("tech_topics", "Vector DB", "run_2")
    temp_feed_store.log_activity("tech_topics", "eBPF", "run_3")
    temp_feed_store.log_activity("stock_market", "NVDA", "run_4")

    recent = temp_feed_store.get_recent_searches(limit=10)
    assert len(recent) == 4

    # Check top trends
    tech_trends = temp_feed_store.get_top_trends(domain="tech_topics", limit=5)
    assert len(tech_trends) == 2
    # Vector DB should rank higher due to 2 queries vs 1
    assert tech_trends[0].query_text == "Vector DB"
    assert tech_trends[0].count == 2
    assert tech_trends[1].query_text == "eBPF"

def test_bookmarks_crud(temp_feed_store):
    bm = temp_feed_store.add_bookmark(
        domain="tech_topics",
        item_type="tech_summary",
        title="Vector DB Deep Dive",
        reference_path="outputs/run_1/summaries/vector_db.md",
        summary="A deep dive into vector search",
        tags=["#VectorDB", "#Search"],
        metadata={"reading_time": 5}
    )
    assert bm.id is not None
    assert bm.title == "Vector DB Deep Dive"
    assert temp_feed_store.is_bookmarked("outputs/run_1/summaries/vector_db.md")

    # List bookmarks
    all_bms = temp_feed_store.list_bookmarks()
    assert len(all_bms) == 1
    assert all_bms[0].tags == ["#VectorDB", "#Search"]

    # Delete bookmark
    deleted = temp_feed_store.delete_bookmark(bm.id)
    assert deleted is True
    assert temp_feed_store.list_bookmarks() == []
    assert not temp_feed_store.is_bookmarked("outputs/run_1/summaries/vector_db.md")

def test_missed_questions_spaced_repetition(temp_feed_store):
    # Add a missed question
    q = temp_feed_store.add_missed_question(
        title="Alien Dictionary",
        category="DSA",
        company="Meta",
        what_tripped_me="Topological sort cycle detection",
        difficulty="Hard"
    )
    assert q.id is not None
    assert q.mastery_level == 0
    assert q.review_count == 0

    # Advance review with mastery level 1
    updated = temp_feed_store.update_missed_question(
        question_id=q.id,
        mastery_level=1,
        advance_review=True
    )
    assert updated.mastery_level == 1
    assert updated.review_count == 1
    assert updated.next_review_due is not None

    # Mark as mastered (mastery 2)
    mastered = temp_feed_store.update_missed_question(
        question_id=q.id,
        mastery_level=2,
        advance_review=True
    )
    assert mastered.mastery_level == 2
    assert mastered.review_count == 2

    # Should not show in due_only list
    due_items = temp_feed_store.list_missed_questions(due_only=True)
    assert len(due_items) == 0

def test_telemetry_auto_ingestion(temp_feed_store):
    # Log 1 stumble
    t1 = temp_feed_store.log_telemetry(
        topic_slug="raft_consensus",
        game_type="flashcards",
        result="stumbled",
        feedback_notes="Failed election timer question"
    )
    assert t1.id is not None
    # Still 0 missed questions
    assert len(temp_feed_store.list_missed_questions()) == 0

    # Log 2nd stumble on same topic -> should auto-create a missed question!
    temp_feed_store.log_telemetry(
        topic_slug="raft_consensus",
        game_type="flashcards",
        result="stumbled"
    )
    missed = temp_feed_store.list_missed_questions()
    assert len(missed) == 1
    assert "Raft Consensus" in missed[0].title
    assert missed[0].source == "flashcard_game"

def test_stock_watchlist(temp_feed_store):
    temp_feed_store.upsert_stock_watchlist(
        ticker="NVDA",
        company_name="NVIDIA Corporation",
        current_price=120.0,
        dcf_target_price=145.0,
        dcf_upside_percent=20.8,
        conviction="High Conviction",
        critic_warning="CapEx concentration"
    )
    watchlist = temp_feed_store.list_stock_watchlist()
    assert len(watchlist) == 1
    assert watchlist[0].ticker == "NVDA"
    assert watchlist[0].dcf_upside_percent == 20.8

def test_feed_service_assembly(temp_feed_store):
    with tempfile.TemporaryDirectory() as tmp_out:
        service = FeedService(feed_store=temp_feed_store, outputs_path=Path(tmp_out))
        feed = service.get_home_feed()
        assert feed.hero_workout is not None
        assert feed.tech_radar is not None
        assert feed.stock_radar is not None
        assert feed.interview_radar is not None
