import tempfile
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from research_agent.models import FlashcardItem, FlashcardsGame, ResearchNotes, TopicSummary
from research_agent.agents.gamification_agent import GamificationAgent
from research_agent.llm.mock_provider import MockProvider
from research_agent.storage import RunStore
from research_agent.storage.run_tracker import RUNS_DB
from research_agent.web.app import app

client = TestClient(app)

def test_gamification_models():
    card = FlashcardItem(
        id="card_1",
        category="Architecture",
        difficulty="Medium",
        front_prompt="How does MCP communicate with tools?",
        back_explanation="Uses JSON-RPC 2.0 over stdio or SSE.",
        hint="Consider transport primitives.",
        key_takeaway="JSON-RPC 2.0 is the foundational protocol."
    )
    assert card.id == "card_1"
    assert card.difficulty == "Medium"
    
    game = FlashcardsGame(
        topic="Model Context Protocol (MCP)",
        game_type="flashcards",
        total_cards=1,
        cards=[card]
    )
    assert game.topic == "Model Context Protocol (MCP)"
    assert len(game.cards) == 1

def test_gamification_agent_generation():
    llm = MockProvider()
    agent = GamificationAgent(llm)
    
    notes = ResearchNotes(
        topic="Model Context Protocol (MCP)",
        definition="An open protocol standardizing tool connectivity.",
        why_it_matters=["Solves N-to-M integration"],
        technical_details=["stdio and SSE transports"],
        examples=["Postgres MCP Server"],
        use_cases=["AI Coding Assistants"],
        limitations=["Early spec"],
        related_topics=["JSON-RPC"],
        sources=[]
    )
    
    game = agent.generate_game("Model Context Protocol (MCP)", research_notes=notes, game_type="flashcards")
    assert isinstance(game, FlashcardsGame)
    assert len(game.cards) > 0
    assert game.cards[0].front_prompt != ""

def test_run_store_game_persistence():
    with tempfile.TemporaryDirectory() as tmp_dir:
        store = RunStore(outputs_dir=tmp_dir)
        run_id = store.create_run("test_game_run")
        
        card = FlashcardItem(
            id="card_1",
            category="Trade-offs",
            difficulty="Hard",
            front_prompt="What are HNSW index memory trade-offs?",
            back_explanation="HNSW requires all vector graphs in RAM.",
            hint="Think about memory vs disk.",
            key_takeaway="High recall requires high RAM."
        )
        game = FlashcardsGame(topic="Vector Databases", total_cards=1, cards=[card])
        
        store.save_game("vector_databases", "flashcards", game)
        assert (store.games_path / "vector_databases_flashcards.json").exists()
        
        loaded = store.load_game("vector_databases", "flashcards")
        assert loaded is not None
        assert loaded["topic"] == "Vector Databases"
        assert len(loaded["cards"]) == 1
        
        games_list = store.list_games()
        assert len(games_list) == 1
        assert games_list[0]["game_type"] == "flashcards"

def test_gamification_api_endpoints():
    run_id = "test_run_games"
    RUNS_DB[run_id] = {
        "status": "completed",
        "progress": 100,
        "current_step": "Completed",
        "interests": "AI infrastructure",
        "raw_topics": [],
        "refined_topics": [],
        "selected_topics": ["Model Context Protocol (MCP)"],
        "final_pack": "# MCP Pack",
        "error": None
    }
    
    with patch("research_agent.web.app.get_llm_provider", return_value=MockProvider()):
        # 1. Test get or generate topic flashcards
        res = client.get(f"/api/runs/{run_id}/topics/model_context_protocol_mcp/games/flashcards")
        assert res.status_code == 200
        data = res.json()
        assert data["game_type"] == "flashcards"
        assert len(data["cards"]) > 0
        
        # 2. Test list games endpoint
        res_list = client.get(f"/api/runs/{run_id}/games")
        assert res_list.status_code == 200
        assert "supported_game_types" in res_list.json()
        assert "flashcards" in res_list.json()["supported_game_types"]
