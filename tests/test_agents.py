import pytest
from unittest.mock import patch
from research_agent.llm.mock_provider import MockProvider
from research_agent.models import TopicCandidate, RefinedTopic, ResearchNotes, TopicSummary
from research_agent.agents.topic_agent import TopicAgent
from research_agent.agents.fine_tuner_agent import FineTunerAgent, compute_final_score
from research_agent.agents.researcher_agent import ResearcherAgent
from research_agent.agents.summariser_agent import SummariserAgent

@pytest.fixture
def mock_llm():
    return MockProvider()

def test_topic_agent_discovery(mock_llm):
    with patch("research_agent.agents.topic_agent.search_web", return_value=[
        {"title": "Test Title", "url": "https://example.com/test", "snippet": "Test snippet"}
    ]):
        agent = TopicAgent(mock_llm)
        topics = agent.discover_topics("AI Infrastructure, distributed systems", max_candidates=2)
        assert len(topics) > 0
        assert isinstance(topics[0], TopicCandidate)
        assert topics[0].title == "Model Context Protocol (MCP)"

def test_fine_tuner_agent_refinement(mock_llm):
    candidates = [
        TopicCandidate(
            title="Model Context Protocol (MCP)",
            short_description="An open standard unifying AI data integration.",
            category="AI Infrastructure",
            trend_reason="Rapid adoption.",
            evidence_sources=["https://modelcontextprotocol.io"],
            estimated_interview_value=9,
            trend_score=9
        ),
        TopicCandidate(
            title="Vector Databases",
            short_description="Databases for vector search.",
            category="Databases",
            trend_reason="RAG scaling.",
            evidence_sources=["https://qdrant.tech"],
            estimated_interview_value=8,
            trend_score=8
        )
    ]
    agent = FineTunerAgent(mock_llm)
    refined = agent.refine_topics(
        user_interests="AI Infrastructure",
        candidates=candidates,
        max_selected=2
    )
    assert len(refined) == 2
    assert isinstance(refined[0], RefinedTopic)
    assert refined[0].title == "Model Context Protocol (MCP)"

def test_compute_final_score():
    scores = {
        "interest_match": 10,
        "interview_value": 10,
        "depth": 10,
        "freshness": 10,
        "source_quality": 10
    }
    score = compute_final_score(scores)
    assert score == 10.0

def test_researcher_agent(mock_llm):
    refined = RefinedTopic(
        title="Model Context Protocol (MCP)",
        reason_selected="Top match for developer tooling.",
        relevance_to_user="Matches developer tools.",
        expected_learning_outcome="Master client-server architecture.",
        scores={"interest_match": 9, "interview_value": 9},
        source_urls=["https://modelcontextprotocol.io"]
    )
    with patch("research_agent.agents.researcher_agent.search_web", return_value=[
        {"title": "MCP Spec", "url": "https://modelcontextprotocol.io", "snippet": "Spec snippet"}
    ]), patch("research_agent.agents.researcher_agent.scrape_url", return_value="Detailed scraped text about MCP."):
        agent = ResearcherAgent(mock_llm)
        notes = agent.research_topic(refined, max_sources=2)
        assert isinstance(notes, ResearchNotes)
        assert notes.topic == "Model Context Protocol (MCP)"
        assert len(notes.technical_details) > 0

def test_summariser_agent(mock_llm):
    notes = ResearchNotes(
        topic="Model Context Protocol (MCP)",
        definition="An open protocol for LLM tool integration.",
        why_it_matters=["Standardizes agent connections"],
        technical_details=["JSON-RPC 2.0 transport over stdio and SSE"],
        examples=["Database connection server"],
        use_cases=["Coding assistants"],
        limitations=["Early ecosystem"],
        related_topics=["LSP", "JSON-RPC"],
        sources=[]
    )
    agent = SummariserAgent(mock_llm)
    summary = agent.summarize_research(notes)
    assert isinstance(summary, TopicSummary)
    assert summary.topic == "Model Context Protocol (MCP)"
    assert "## One-Line Explanation" in summary.summary_markdown
