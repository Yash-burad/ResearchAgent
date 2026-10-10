import threading
from pathlib import Path
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from research_agent.graph import create_research_graph
from research_agent.storage import RunStore
from research_agent.storage.run_tracker import RUNS_DB
from research_agent.models import (
    TopicCandidate,
    RefinedTopic,
    ResearchNotes,
    TopicSummary,
    FlashcardsGame,
    CompanyInterviewIntel,
    InterviewSession,
    InterviewFeedback,
    StartSessionRequest,
    SendMessageRequest
)
from research_agent.agents.gamification_agent import GamificationAgent
from research_agent.agents.mock_interviewer_agent import MockInterviewerAgent
from research_agent.llm import get_llm_provider
from research_agent.storage.markdown_writer import slugify
from research_agent.services.feed_service import FeedService
from research_agent.models.feed import (
    CreateBookmarkRequest,
    CreateMissedQuestionRequest,
    UpdateMissedQuestionRequest,
    LogTelemetryRequest
)


app = FastAPI(title="AI Research Agent API")
feed_service = FeedService()

# Enable CORS for development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


class CreateRunRequest(BaseModel):
    mode: str = "tech_topics"  # "tech_topics", "interview_experience", or "stock_market"
    research_mode: Optional[str] = None
    interests: Optional[str] = ""
    company_name: Optional[str] = None
    target_role: Optional[str] = None
    target_level: Optional[str] = None
    manual_selection: bool = False

    # Stock Market Intelligence fields
    stock_mode: Optional[str] = "stock_research"  # "stock_research" or "stock_picks"
    stock_sub_mode: Optional[str] = None
    ticker: Optional[str] = None
    stock_ticker: Optional[str] = None
    manual_peers: Optional[List[str]] = None
    investment_horizon: Optional[str] = "3-5 Years"
    stock_investment_horizon: Optional[str] = None
    stock_risk_profile: Optional[str] = None
    stock_asset_class: Optional[str] = None
    stock_market_cap_tier: Optional[str] = None
    sector_filter: Optional[str] = None

class SelectTopicsRequest(BaseModel):
    selected_topics: List[str]

class GenerateGameRequest(BaseModel):
    game_type: str = "flashcards"

def run_graph_in_background(run_id: str, state: dict):
    try:
        graph = create_research_graph()
        graph.invoke(state)
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Background thread execution failed: {error_msg}")
        if run_id in RUNS_DB:
            RUNS_DB[run_id]["status"] = "failed"
            RUNS_DB[run_id]["error"] = str(e)

@app.post("/api/runs")
def create_run(req: CreateRunRequest):
    store = RunStore()
    run_id = store.create_run()
    
    effective_mode = req.research_mode or req.mode
    effective_stock_mode = req.stock_sub_mode or req.stock_mode
    effective_ticker = req.stock_ticker or req.ticker
    effective_horizon = req.stock_investment_horizon or req.investment_horizon
    # Log activity for the home page feed
    query_text = (
        effective_ticker if effective_mode == "stock_market"
        else (req.company_name if effective_mode == "interview_experience" else req.interests)
    )
    if query_text:
        feed_service.store.log_activity(domain=effective_mode, query_text=query_text, run_id=run_id)

    # Initialize tracker in-memory database
    RUNS_DB[run_id] = {
        "status": "discovering" if effective_mode == "tech_topics" else "researching",
        "progress": 0,
        "current_step": "Initializing run...",
        "research_mode": effective_mode,
        "interests": req.interests or "",
        "company_name": req.company_name,
        "target_role": req.target_role,
        "target_level": req.target_level,
        "stock_mode": effective_stock_mode,
        "stock_sub_mode": effective_stock_mode,
        "ticker": effective_ticker,
        "stock_ticker": effective_ticker,
        "stock_asset_class": req.stock_asset_class,
        "stock_market_cap_tier": req.stock_market_cap_tier,
        "raw_topics": [],
        "refined_topics": [],
        "selected_topics": [],
        "final_pack": "",
        "interview_intel": None,
        "stock_research_report": None,
        "stock_opportunity_report": None,
        "error": None
    }
    
    initial_state = {
        "research_mode": effective_mode,
        "company_name": req.company_name,
        "target_role": req.target_role,
        "target_level": req.target_level,
        "user_interests": req.interests or (effective_ticker or ""),
        "target_audience": "Mid-Senior Level",
        "stock_mode": effective_stock_mode,
        "ticker": effective_ticker or req.interests or "NVDA",
        "manual_peers": req.manual_peers,
        "investment_horizon": effective_horizon,
        "sector_filter": req.sector_filter,
        "raw_topics": [],
        "refined_topics": [],
        "selected_topics": [],
        "research_notes": {},
        "summaries": {},
        "errors": [],
        "run_id": run_id,
        "manual_selection": req.manual_selection
    }
    
    # Start graph execution in a background thread to prevent API blocking
    threading.Thread(
        target=run_graph_in_background,
        args=(run_id, initial_state),
        daemon=True
    ).start()
    
    return {"run_id": run_id}

@app.get("/api/runs/{run_id}")
def get_run_status(run_id: str):
    if run_id not in RUNS_DB:
        raise HTTPException(status_code=404, detail="Run not found")
    return RUNS_DB[run_id]

@app.get("/api/runs/{run_id}/stock-research")
def get_stock_research(run_id: str):
    store = RunStore()
    store.set_run(run_id)
    data = store.load_stock_research()
    if not data:
        if run_id in RUNS_DB and RUNS_DB[run_id].get("stock_research_report"):
            return RUNS_DB[run_id]["stock_research_report"]
        raise HTTPException(status_code=404, detail="Stock research report not found for this run")
    return data

@app.get("/api/runs/{run_id}/stock-picks")
def get_stock_picks(run_id: str):
    store = RunStore()
    store.set_run(run_id)
    data = store.load_stock_picks()
    if not data:
        if run_id in RUNS_DB and RUNS_DB[run_id].get("stock_opportunity_report"):
            return RUNS_DB[run_id]["stock_opportunity_report"]
        raise HTTPException(status_code=404, detail="Stock opportunity report not found for this run")
    return data

@app.post("/api/runs/{run_id}/select-topics")
def select_topics(run_id: str, req: SelectTopicsRequest):
    if run_id not in RUNS_DB:
        raise HTTPException(status_code=404, detail="Run not found")
    
    run_info = RUNS_DB[run_id]
    if run_info["status"] != "pending_selection":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot select topics when run status is: {run_info['status']}"
        )
    
    # Parse existing models from stored raw lists
    raw_topics = [TopicCandidate(**x) for x in run_info["raw_topics"]]
    refined_topics = [RefinedTopic(**x) for x in run_info["refined_topics"]]
    
    # Create resume state
    resume_state = {
        "user_interests": run_info["interests"],
        "target_audience": "Mid-Senior Level",
        "raw_topics": raw_topics,
        "refined_topics": refined_topics,
        "selected_topics": req.selected_topics,
        "research_notes": {},
        "summaries": {},
        "errors": [],
        "run_id": run_id,
        "manual_selection": True
    }
    
    # Update tracker state
    run_info["status"] = "researching"
    run_info["progress"] = 55
    run_info["selected_topics"] = req.selected_topics
    run_info["current_step"] = "Resuming execution with selected topics..."
    
    # Resume pipeline in background thread
    threading.Thread(
        target=run_graph_in_background,
        args=(run_id, resume_state),
        daemon=True
    ).start()
    
    return {"status": "resumed"}

@app.get("/api/runs/{run_id}/topics")
def get_run_topics(run_id: str):
    if run_id not in RUNS_DB:
        raise HTTPException(status_code=404, detail="Run not found")
    run_info = RUNS_DB[run_id]
    return {
        "raw_topics": run_info.get("raw_topics", []),
        "refined_topics": run_info.get("refined_topics", []),
        "selected_topics": run_info.get("selected_topics", [])
    }

@app.get("/api/runs/{run_id}/final-pack")
def get_final_pack(run_id: str):
    if run_id not in RUNS_DB:
        raise HTTPException(status_code=404, detail="Run not found")
    run_info = RUNS_DB[run_id]
    final_pack = run_info.get("final_pack", "")
    if not final_pack:
        store = RunStore()
        pack_file = store.outputs_dir / run_id / "final_interview_pack.md"
        if not pack_file.exists():
            pack_file = store.outputs_dir / run_id / "company_interview_pack.md"
        if pack_file.exists():
            final_pack = pack_file.read_text(encoding="utf-8")
    return {
        "run_id": run_id,
        "final_pack": final_pack
    }

@app.get("/api/runs/{run_id}/interview-intel")
def get_interview_intel(run_id: str):
    if run_id not in RUNS_DB:
        raise HTTPException(status_code=404, detail="Run not found")
    run_info = RUNS_DB[run_id]
    intel = run_info.get("interview_intel")
    if not intel:
        store = RunStore()
        store.set_run(run_id)
        intel_obj = store.load_interview_intel()
        if intel_obj:
            intel = intel_obj.model_dump()
    if not intel:
        raise HTTPException(status_code=404, detail="Interview intelligence not found for this run")
    return intel


# ----------------- Gamification Endpoints -----------------

@app.get("/api/runs/{run_id}/games")
def list_run_games(run_id: str):
    store = RunStore()
    store.set_run(run_id)
    return {
        "run_id": run_id,
        "games": store.list_games(),
        "supported_game_types": ["flashcards"]
    }

@app.get("/api/runs/{run_id}/topics/{topic_slug}/games/{game_type}")
def get_topic_game(run_id: str, topic_slug: str, game_type: str = "flashcards"):
    store = RunStore()
    store.set_run(run_id)
    
    # Check if already generated
    cached = store.load_game(topic_slug, game_type)
    if cached:
        return cached

    # Otherwise, generate on demand
    return generate_topic_game_helper(run_id, topic_slug, game_type, store)

@app.post("/api/runs/{run_id}/topics/{topic_slug}/games")
def create_topic_game(run_id: str, topic_slug: str, req: GenerateGameRequest):
    store = RunStore()
    store.set_run(run_id)
    return generate_topic_game_helper(run_id, topic_slug, req.game_type, store)

def generate_topic_game_helper(run_id: str, topic_slug: str, game_type: str, store: RunStore):
    # Locate research notes & summaries if available
    notes = None
    summary = None
    topic_title = topic_slug.replace("_", " ").title()

    # Attempt to load notes and summary from storage
    if store.research_path.exists():
        for f in store.research_path.glob("*.json"):
            if topic_slug in f.stem or f.stem in topic_slug:
                try:
                    notes_dict = store.read_json(f"research/{f.name}")
                    if notes_dict:
                        notes = ResearchNotes(**notes_dict)
                        topic_title = notes.topic
                except Exception:
                    pass

    if store.summaries_path.exists():
        for f in store.summaries_path.glob("*.json"):
            if topic_slug in f.stem or f.stem in topic_slug:
                try:
                    sum_dict = store.read_json(f"summaries/{f.name}")
                    if sum_dict:
                        summary = TopicSummary(**sum_dict)
                        topic_title = summary.topic
                except Exception:
                    pass

    llm = get_llm_provider()
    agent = GamificationAgent(llm)
    game = agent.generate_game(topic_title, notes, summary, game_type=game_type)
    store.save_game(topic_slug, game_type, game)
    
    return game.model_dump() if hasattr(game, "model_dump") else game

# ----------------- Mock Interview Simulation Endpoints -----------------

def _get_run_intel_helper(run_id: str, store: RunStore) -> CompanyInterviewIntel:
    intel_dict = None
    if run_id in RUNS_DB and RUNS_DB[run_id].get("interview_intel"):
        intel_dict = RUNS_DB[run_id]["interview_intel"]
    if not intel_dict:
        intel_dict = store.load_interview_intel()
    
    if intel_dict:
        return CompanyInterviewIntel(**intel_dict)
    
    # Fallback intel if not yet generated or testing custom run
    company = RUNS_DB.get(run_id, {}).get("company_name", "Target Company")
    role = RUNS_DB.get(run_id, {}).get("target_role", "Senior Software Engineer")
    level = RUNS_DB.get(run_id, {}).get("target_level", "Senior / L5")
    return CompanyInterviewIntel(
        company_name=company,
        role=role,
        level=level,
        hiring_bar_summary=f"Rigorous engineering bar for {company} {role} ({level}).",
        rounds_breakdown=[],
        top_dsa_patterns=["LRU Cache", "Tree Traversal", "Rate Limiting"],
        top_system_design_topics=["Distributed Queue", "Idempotent API Gateway"],
        cultural_values_and_behavioral=["Customer Obsession", "High Agency", "Craftsmanship"],
        recent_experiences_summary=["Pragmatic problem solving with focus on production edge cases."],
        sources=[],
        prep_pack_markdown=""
    )

@app.get("/api/runs/{run_id}/interview-sessions")
def list_interview_sessions(run_id: str):
    store = RunStore()
    store.set_run(run_id)
    return {
        "run_id": run_id,
        "sessions": store.list_sessions()
    }

@app.post("/api/runs/{run_id}/interview-sessions")
def start_interview_session(run_id: str, req: StartSessionRequest):
    store = RunStore()
    store.set_run(run_id)
    intel = _get_run_intel_helper(run_id, store)
    
    llm = get_llm_provider()
    agent = MockInterviewerAgent(llm)
    session = agent.start_interview(intel, req.round_name, req.round_type)
    session.run_id = run_id
    
    store.save_session(session)
    return session.model_dump()

@app.get("/api/runs/{run_id}/interview-sessions/{session_id}")
def get_interview_session(run_id: str, session_id: str):
    store = RunStore()
    store.set_run(run_id)
    session_data = store.load_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return session_data

@app.post("/api/runs/{run_id}/interview-sessions/{session_id}/message")
def send_candidate_message(run_id: str, session_id: str, req: SendMessageRequest):
    store = RunStore()
    store.set_run(run_id)
    session_data = store.load_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    session = InterviewSession(**session_data)
    if session.status == "completed":
        raise HTTPException(status_code=400, detail="Cannot send message to a completed interview session")
    
    intel = _get_run_intel_helper(run_id, store)
    llm = get_llm_provider()
    agent = MockInterviewerAgent(llm)
    
    agent.respond(intel, session, req.message)
    store.save_session(session)
    return session.model_dump()

@app.post("/api/runs/{run_id}/interview-sessions/{session_id}/finish")
def finish_interview_session(run_id: str, session_id: str):
    store = RunStore()
    store.set_run(run_id)
    session_data = store.load_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    session = InterviewSession(**session_data)
    intel = _get_run_intel_helper(run_id, store)
    llm = get_llm_provider()
    agent = MockInterviewerAgent(llm)
    
    feedback = agent.evaluate(intel, session)
    store.save_session(session)
    store.save_feedback(session_id, feedback)
    
    # Ingest candidate weak spots into the missed questions stumble log
    feed_service.ingest_mock_interview_feedback(
        company_name=session.company_name,
        round_name=session.round_name,
        feedback_data=feedback.model_dump()
    )
    
    return feedback.model_dump()

@app.get("/api/runs/{run_id}/interview-sessions/{session_id}/feedback")
def get_interview_feedback(run_id: str, session_id: str):
    store = RunStore()
    store.set_run(run_id)
    feedback_data = store.load_feedback(session_id)
    if not feedback_data:
        raise HTTPException(status_code=404, detail="Feedback not found for this session")
    return feedback_data

# ----------------- Agent & Prompt Studio Endpoints -----------------

from research_agent.studio import PromptManager, ChainManager, PipelineConfig
from typing import Dict, Any

class UpdatePromptRequest(BaseModel):
    content: str

class TestPromptRequest(BaseModel):
    variables: Dict[str, Any] = {}
    provider: Optional[str] = None

@app.get("/api/prompts")
def list_prompts():
    return {"prompts": [p.model_dump() for p in PromptManager.list_prompts()]}

@app.get("/api/prompts/{filename}")
def get_prompt(filename: str):
    try:
        return PromptManager.get_prompt(filename).model_dump()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/api/prompts/{filename}")
def update_prompt(filename: str, req: UpdatePromptRequest):
    try:
        return PromptManager.update_prompt(filename, req.content).model_dump()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/prompts/{filename}/reset")
def reset_prompt(filename: str):
    try:
        return PromptManager.reset_prompt(filename).model_dump()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/prompts/{filename}/test")
def test_prompt(filename: str, req: TestPromptRequest):
    try:
        return PromptManager.test_prompt(filename, req.variables, req.provider)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/pipeline/config")
def get_pipeline_config():
    return ChainManager.get_config().model_dump()

@app.put("/api/pipeline/config")
def update_pipeline_config(config: PipelineConfig):
    return ChainManager.update_config(config).model_dump()

@app.get("/api/pipeline/graph")
def get_pipeline_graph():
    return ChainManager.get_graph_schema()

# ----------------- Feed & Knowledge Base Endpoints -----------------

@app.get("/api/feed")
def get_home_feed():
    return feed_service.get_home_feed().model_dump()

@app.get("/api/feed/bookmarks")
def list_bookmarks(domain: Optional[str] = None):
    return [b.model_dump() for b in feed_service.list_bookmarks(domain=domain)]

@app.post("/api/feed/bookmarks")
def add_bookmark(req: CreateBookmarkRequest):
    return feed_service.add_bookmark(req).model_dump()

@app.delete("/api/feed/bookmarks/{bookmark_id}")
def delete_bookmark(bookmark_id: int):
    success = feed_service.delete_bookmark(bookmark_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return {"status": "deleted", "id": bookmark_id}

@app.get("/api/feed/missed-questions")
def list_missed_questions(due_only: bool = False, category: Optional[str] = None):
    return [q.model_dump() for q in feed_service.list_missed_questions(due_only=due_only, category=category)]

@app.post("/api/feed/missed-questions")
def add_missed_question(req: CreateMissedQuestionRequest):
    return feed_service.add_missed_question(req).model_dump()

@app.put("/api/feed/missed-questions/{question_id}")
def update_missed_question(question_id: int, req: UpdateMissedQuestionRequest):
    updated = feed_service.update_missed_question(question_id, req)
    if not updated:
        raise HTTPException(status_code=404, detail="Missed question not found")
    return updated.model_dump()

@app.delete("/api/feed/missed-questions/{question_id}")
def delete_missed_question(question_id: int):
    success = feed_service.delete_missed_question(question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"status": "deleted", "id": question_id}

@app.post("/api/feed/telemetry")
def log_telemetry(req: LogTelemetryRequest):
    return feed_service.log_telemetry(req).model_dump()

@app.post("/api/feed/targeted-workout")
def generate_targeted_workout():
    drill = feed_service.generate_targeted_drill_game()
    return drill.model_dump()

@app.post("/api/feed/watchlist/refresh")
def refresh_watchlist():
    updated = feed_service.refresh_stock_watchlist()
    return [item.model_dump() for item in updated]

@app.get("/api/documents")
def get_document(path: str):
    """
    Safely reads markdown or JSON documents relative to project root or outputs/.
    """
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    target = (project_root / path).resolve()
    # Guard against directory traversal: ensure target is within project_root
    if not str(target).startswith(str(project_root)):
        raise HTTPException(status_code=403, detail="Forbidden file path")
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()
        return {
            "path": path,
            "filename": target.name,
            "content": content,
            "is_markdown": target.suffix == ".md"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount frontend files after API endpoints

static_dir = Path(__file__).parent / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True, exist_ok=True)

app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
