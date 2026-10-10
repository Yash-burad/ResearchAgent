import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from research_agent.models import (
    CompanyInterviewIntel,
    InterviewRound,
    InterviewMessage,
    InterviewSession,
    InterviewFeedback,
    RubricScore
)
from research_agent.llm.mock_provider import MockProvider
from research_agent.agents.mock_interviewer_agent import MockInterviewerAgent
from research_agent.storage import RunStore
from research_agent.web.app import app
from research_agent.storage.run_tracker import RUNS_DB

client = TestClient(app)

@pytest.fixture
def sample_intel():
    return CompanyInterviewIntel(
        company_name="Stripe",
        role="Staff Backend Engineer",
        level="Staff / L6",
        hiring_bar_summary="Pragmatic engineering execution and high ownership.",
        rounds_breakdown=[
            InterviewRound(
                round_name="Practical Bug Squash / Integration",
                round_type="Practical / Bug Squash / API",
                duration_minutes=60,
                focus_areas=["Debugging", "Unit Testing"],
                sample_questions=["Fix race condition in billing orchestrator"],
                evaluation_criteria=["Speed of navigation", "Clean fixes", "Test coverage"],
                tips=["Run tests first"]
            ),
            InterviewRound(
                round_name="Distributed System Design",
                round_type="System Design",
                duration_minutes=60,
                focus_areas=["Idempotency", "Consistency"],
                sample_questions=["Design a global idempotent payment processing API"],
                evaluation_criteria=["Distributed locking", "API contracts"],
                tips=["Clarify functional requirements first"]
            )
        ],
        top_dsa_patterns=["LRU Cache", "Linked Hash Maps"],
        top_system_design_topics=["Idempotent payment pipeline"],
        cultural_values_and_behavioral=["Macro optimism, micro pessimism", "High agency"],
        recent_experiences_summary=["Pragmatic focus with local IDE debugging."],
        sources=[],
        prep_pack_markdown="# Stripe Staff Pack"
    )

def test_simulation_models():
    msg = InterviewMessage(
        id="msg_001",
        role="interviewer",
        content="Welcome to your Stripe interview."
    )
    assert msg.role == "interviewer"
    assert msg.id == "msg_001"

    session = InterviewSession(
        session_id="session_123",
        run_id="run_123",
        company_name="Stripe",
        role="Staff Backend Engineer",
        level="Staff / L6",
        round_name="Practical Bug Squash",
        round_type="Practical / Bug Squash / API",
        evaluation_criteria=["Test coverage"],
        messages=[msg],
        status="in_progress"
    )
    assert len(session.messages) == 1
    assert session.status == "in_progress"

    feedback = InterviewFeedback(
        overall_score=90,
        hire_recommendation="Strong Hire",
        summary_verdict="Candidate excelled in system design.",
        rubric_scores=[
            RubricScore(criterion="Technical Depth", score=5, feedback="Outstanding depth.")
        ],
        key_strengths=["Clean modular API"],
        areas_for_improvement=["Cache eviction sizing"],
        culture_fit_notes="Exceptional ownership.",
        detailed_debrief_markdown="# Detailed Debrief"
    )
    assert feedback.overall_score == 90
    assert feedback.hire_recommendation == "Strong Hire"

def test_mock_interviewer_agent_flow(sample_intel):
    mock_llm = MockProvider()
    agent = MockInterviewerAgent(mock_llm)

    # 1. Start session
    session = agent.start_interview(sample_intel, "Distributed System Design")
    assert isinstance(session, InterviewSession)
    assert session.company_name == "Stripe"
    assert len(session.messages) == 1
    assert session.messages[0].role == "interviewer"

    # 2. Respond to candidate message
    candidate_answer = "I would propose an Idempotency-Key header stored in Redis with a 24-hour TTL and SETNX lock."
    response_text = agent.respond(sample_intel, session, candidate_answer)
    assert isinstance(response_text, str)
    assert len(session.messages) == 3
    assert session.messages[1].role == "candidate"
    assert session.messages[2].role == "interviewer"

    # 3. Evaluate interview
    feedback = agent.evaluate(sample_intel, session)
    assert isinstance(feedback, InterviewFeedback)
    assert feedback.overall_score > 0
    assert feedback.hire_recommendation in ["Strong Hire", "Hire", "Lean Hire", "Lean No Hire", "No Hire"]
    assert len(feedback.rubric_scores) > 0
    assert session.status == "completed"

def test_run_store_session_persistence(tmp_path):
    store = RunStore()
    run_id = store.create_run()

    session = InterviewSession(
        session_id="sess_test_999",
        run_id=run_id,
        company_name="Meta",
        role="Senior SWE",
        level="E5",
        round_name="Architecture",
        round_type="System Design",
        evaluation_criteria=["Scalability"],
        messages=[InterviewMessage(id="m1", role="interviewer", content="Design Instagram Feed.")],
        status="in_progress"
    )

    store.save_session(session)
    loaded = store.load_session("sess_test_999")
    assert loaded is not None
    assert loaded["session_id"] == "sess_test_999"
    assert loaded["company_name"] == "Meta"

    sessions_list = store.list_sessions()
    assert len(sessions_list) >= 1
    assert sessions_list[0]["session_id"] == "sess_test_999"

    feedback = InterviewFeedback(
        overall_score=85,
        hire_recommendation="Hire",
        summary_verdict="Solid design.",
        rubric_scores=[],
        key_strengths=["Fanout on write logic"],
        areas_for_improvement=[],
        culture_fit_notes="",
        detailed_debrief_markdown=""
    )
    store.save_feedback("sess_test_999", feedback)
    loaded_feedback = store.load_feedback("sess_test_999")
    assert loaded_feedback is not None
    assert loaded_feedback["overall_score"] == 85

def test_web_api_mock_interview_lifecycle(sample_intel):
    run_id = "test_run_sim_api"
    RUNS_DB[run_id] = {
        "status": "completed",
        "progress": 100,
        "current_step": "Finished",
        "interests": "",
        "company_name": "Stripe",
        "target_role": "Staff Backend Engineer",
        "target_level": "Staff / L6",
        "raw_topics": [],
        "refined_topics": [],
        "selected_topics": ["Stripe (Staff Backend Engineer)"],
        "final_pack": "# Stripe Pack",
        "interview_intel": sample_intel.model_dump(),
        "error": None
    }

    store = RunStore()
    store.set_run(run_id)
    store.save_interview_intel(sample_intel)

    with patch("research_agent.web.app.get_llm_provider", return_value=MockProvider()):
        # 1. Start Session
        start_res = client.post(f"/api/runs/{run_id}/interview-sessions", json={
            "round_name": "Distributed System Design",
            "round_type": "System Design"
        })
        assert start_res.status_code == 200
        session_data = start_res.json()
        session_id = session_data["session_id"]
        assert len(session_data["messages"]) == 1

        # 2. Get Session
        get_res = client.get(f"/api/runs/{run_id}/interview-sessions/{session_id}")
        assert get_res.status_code == 200
        assert get_res.json()["session_id"] == session_id

        # 3. Send Candidate Message
        msg_res = client.post(f"/api/runs/{run_id}/interview-sessions/{session_id}/message", json={
            "message": "We will use Redis distributed lock with lease renewal."
        })
        assert msg_res.status_code == 200
        updated_session = msg_res.json()
        assert len(updated_session["messages"]) == 3

        # 4. Finish Session & Get Scorecard
        finish_res = client.post(f"/api/runs/{run_id}/interview-sessions/{session_id}/finish")
        assert finish_res.status_code == 200
        feedback_data = finish_res.json()
        assert "overall_score" in feedback_data
        assert "hire_recommendation" in feedback_data

        # 5. Retrieve Feedback
        fb_res = client.get(f"/api/runs/{run_id}/interview-sessions/{session_id}/feedback")
        assert fb_res.status_code == 200
        assert fb_res.json()["overall_score"] == feedback_data["overall_score"]
