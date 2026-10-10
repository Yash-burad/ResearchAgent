import tempfile
import pytest
from pathlib import Path
from research_agent.models import TopicCandidate, RefinedTopic, ResearchNotes, ResearchSource, TopicSummary
from research_agent.storage import (
    RunStore,
    write_trending_topics_md,
    write_refined_topics_md,
    write_research_notes_md,
    write_summary_md,
    write_final_interview_pack_md
)

def test_storage_and_markdown_writers():
    # Use temporary directory for testing
    with tempfile.TemporaryDirectory() as tmp_dir:
        store = RunStore(outputs_dir=tmp_dir)
        run_id = store.create_run("test_run")
        
        assert run_id == "test_run"
        assert store.run_path.exists()
        assert store.research_path.exists()
        assert store.summaries_path.exists()
        
        # 1. Topic Candidates
        tc = TopicCandidate(
            title="Model Context Protocol",
            short_description="Open standard to connect LLMs to data.",
            category="AI Infra",
            trend_reason="Rapid adoption by Anthropic and developer tools.",
            evidence_sources=["https://example.com/mcp-news"],
            estimated_interview_value=8,
            trend_score=9
        )
        store.save_trending_topics([tc])
        assert (store.run_path / "trending_topics.json").exists()
        
        write_trending_topics_md([tc], store)
        assert (store.run_path / "trending_topics.md").exists()
        
        # 2. Refined Topics
        rt = RefinedTopic(
            title="Model Context Protocol",
            reason_selected="Highly relevant to developer tooling and infrastructure.",
            relevance_to_user="Matches developer tools interest.",
            expected_learning_outcome="Understand MCP protocol and Client-Server architecture.",
            scores={"interest_match": 9, "interview_value": 8},
            source_urls=["https://example.com/mcp-news"]
        )
        store.save_refined_topics([rt])
        assert (store.run_path / "refined_topics.json").exists()
        
        write_refined_topics_md([rt], store)
        assert (store.run_path / "refined_topics.md").exists()
        
        # 3. Research Notes
        rs = ResearchSource(
            url="https://example.com/mcp-news",
            title="MCP Launch",
            publisher="Anthropic Blog",
            extracted_at="2026-06-13",
            credibility_score=9,
            key_points=["MCP uses JSON-RPC over stdio or SSE."]
        )
        notes = ResearchNotes(
            topic="Model Context Protocol",
            definition="An open protocol standard.",
            why_it_matters=["Standardizes agent tool use"],
            technical_details=["Client-server protocol using JSON-RPC"],
            examples=["Python MCP SDK server setup"],
            use_cases=["AI editors connecting to database"],
            limitations=["Connection latency"],
            related_topics=["JSON-RPC", "WebSockets"],
            sources=[rs]
        )
        store.save_research_notes("topic_1_mcp", notes)
        assert (store.research_path / "topic_1_mcp.json").exists()
        
        slug = write_research_notes_md(notes, 1, store)
        assert slug == "topic_1_model_context_protocol"
        assert (store.research_path / "topic_1_model_context_protocol.md").exists()
        
        # 4. Summaries
        summary = TopicSummary(
            topic="Model Context Protocol",
            summary_markdown="# Model Context Protocol\n\n## One-Line Explanation\nA protocol for AI agent tools."
        )
        store.save_summary("topic_1_mcp", summary)
        assert (store.summaries_path / "topic_1_mcp.json").exists()
        
        slug2 = write_summary_md(summary, 1, store)
        assert slug2 == "topic_1_model_context_protocol"
        assert (store.summaries_path / "topic_1_model_context_protocol.md").exists()
        
        write_final_interview_pack_md([summary], store)
        assert (store.run_path / "final_interview_pack.md").exists()
