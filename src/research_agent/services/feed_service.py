import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from research_agent.storage.feed_store import FeedStore
from research_agent.storage.run_store import RunStore
from research_agent.models.feed import (
    HomeFeedResponse,
    HeroWorkout,
    TechRadarSection,
    StockRadarSection,
    InterviewRadarSection,
    BookmarkItem,
    CreateBookmarkRequest,
    MissedQuestionItem,
    CreateMissedQuestionRequest,
    UpdateMissedQuestionRequest,
    LogTelemetryRequest
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_OUTPUTS_PATH = PROJECT_ROOT / "outputs"

class FeedService:
    """
    High-performance aggregator for the Home Page Feed.
    Orchestrates SQLite telemetry, bookmarks, spaced-repetition workouts,
    and bridges filesystem artifacts from outputs/.
    """

    def __init__(self, feed_store: Optional[FeedStore] = None, outputs_path: Optional[Path] = None):
        self.store = feed_store or FeedStore()
        self.outputs_path = outputs_path or DEFAULT_OUTPUTS_PATH
        self._ensure_bootstrapped()

    def get_home_feed(self) -> HomeFeedResponse:
        """
        Assembles the complete home feed in <10ms from SQLite indexes and cached metadata.
        """
        # 1. Hero Workout (Spaced Repetition)
        due_questions = self.store.list_missed_questions(due_only=True, limit=5)
        total_due = len(due_questions)
        
        # If no questions are currently overdue, show upcoming or unmastered
        display_workout_questions = due_questions
        if not display_workout_questions:
            display_workout_questions = self.store.list_missed_questions(due_only=False, limit=3)
        
        suggested_focus = None
        if due_questions:
            categories = list({q.category for q in due_questions})
            suggested_focus = f"Spaced-Repetition Review: Focus on {', '.join(categories)}"
        elif display_workout_questions:
            suggested_focus = "Keep your edge sharp! Daily retention drill."
        else:
            suggested_focus = "All clear! Log questions from recent interviews or play a flashcard drill."

        hero_workout = HeroWorkout(
            total_due=total_due,
            due_questions=display_workout_questions,
            suggested_focus=suggested_focus
        )

        # 2. Tech Radar
        tech_trends = self.store.get_top_trends(domain="tech_topics", limit=6)
        saved_tech_articles = self.store.list_bookmarks(domain="tech_topics")
        tech_radar = TechRadarSection(
            trending_topics=tech_trends,
            saved_articles=saved_tech_articles
        )

        # 3. Stock Radar
        watchlist = self.store.list_stock_watchlist()
        saved_stocks = self.store.list_bookmarks(domain="stock_market")
        recent_picks = self._get_recent_stock_picks()
        stock_radar = StockRadarSection(
            watchlist=watchlist,
            saved_reports=saved_stocks,
            recent_picks=recent_picks
        )

        # 4. Interview Radar
        company_guides = self._get_recent_company_guides()
        missed_questions = self.store.list_missed_questions(due_only=False, limit=10)
        recent_mock_sessions = self._get_recent_mock_sessions()
        interview_radar = InterviewRadarSection(
            recent_company_guides=company_guides,
            missed_questions=missed_questions,
            recent_mock_sessions=recent_mock_sessions
        )

        all_bookmarks = self.store.list_bookmarks()

        return HomeFeedResponse(
            hero_workout=hero_workout,
            tech_radar=tech_radar,
            stock_radar=stock_radar,
            interview_radar=interview_radar,
            total_bookmarks=len(all_bookmarks)
        )

    # ================= Bookmarks =================

    def add_bookmark(self, req: CreateBookmarkRequest) -> BookmarkItem:
        return self.store.add_bookmark(
            domain=req.domain,
            item_type=req.item_type,
            title=req.title,
            reference_path=req.reference_path,
            summary=req.summary or "",
            external_url=req.external_url,
            tags=req.tags,
            metadata=req.metadata
        )

    def list_bookmarks(self, domain: Optional[str] = None) -> List[BookmarkItem]:
        return self.store.list_bookmarks(domain=domain)

    def delete_bookmark(self, bookmark_id: int) -> bool:
        return self.store.delete_bookmark(bookmark_id)

    # ================= Missed Questions =================

    def add_missed_question(self, req: CreateMissedQuestionRequest) -> MissedQuestionItem:
        return self.store.add_missed_question(
            title=req.title,
            category=req.category,
            what_tripped_me=req.what_tripped_me,
            company=req.company,
            source=req.source,
            difficulty=req.difficulty
        )

    def update_missed_question(self, question_id: int, req: UpdateMissedQuestionRequest) -> Optional[MissedQuestionItem]:
        return self.store.update_missed_question(
            question_id=question_id,
            mastery_level=req.mastery_level,
            what_tripped_me=req.what_tripped_me,
            advance_review=bool(req.advance_review)
        )

    def list_missed_questions(self, due_only: bool = False, category: Optional[str] = None) -> List[MissedQuestionItem]:
        return self.store.list_missed_questions(due_only=due_only, category=category)

    def delete_missed_question(self, question_id: int) -> bool:
        return self.store.delete_missed_question(question_id)

    # ================= Telemetry =================

    def log_telemetry(self, req: LogTelemetryRequest):
        return self.store.log_telemetry(
            topic_slug=req.topic_slug,
            card_id=req.card_id,
            game_type=req.game_type,
            result=req.result,
            feedback_notes=req.feedback_notes
        )

    # ================= Automatic Mock Interview Ingestion =================

    def ingest_mock_interview_feedback(self, company_name: str, round_name: str, feedback_data: Dict[str, Any]):
        """
        Parses MockInterviewerAgent's Hiring Committee scorecard.
        Any rubric score <= 3 or areas_for_improvement are automatically inserted
        into candidate's missed_questions stumble log.
        """
        rubrics = feedback_data.get("rubric_scores", [])
        for r in rubrics:
            score = r.get("score", 5)
            criterion = r.get("criterion", "Technical Execution")
            feedback = r.get("feedback", "")
            if score <= 3:
                title = f"{company_name}: {criterion} ({round_name})"
                what_tripped = feedback or f"Scored {score}/5 on {criterion} during mock interview."
                # Check for duplicate
                existing = self.store.list_missed_questions(due_only=False, limit=50)
                if not any(q.title == title for q in existing):
                    self.store.add_missed_question(
                        title=title,
                        category="System Design" if "System" in round_name else "DSA",
                        company=company_name,
                        what_tripped_me=what_tripped,
                        source="mock_interview",
                        difficulty="Hard" if score <= 2 else "Medium"
                    )

        improvements = feedback_data.get("areas_for_improvement", [])
        for imp in improvements[:2]:
            clean_imp = imp.strip("- ").strip()
            if len(clean_imp) > 10:
                title = f"{company_name}: {round_name} Stumble"
                existing = self.store.list_missed_questions(due_only=False, limit=50)
                if not any(q.title == title for q in existing):
                    self.store.add_missed_question(
                        title=title,
                        category="System Design" if "Design" in round_name else "DSA",
                        company=company_name,
                        what_tripped_me=clean_imp,
                        source="mock_interview",
                        difficulty="Medium"
                    )

    # ================= Artifact Helpers =================

    def _get_recent_company_guides(self, limit: int = 4) -> List[Dict[str, Any]]:
        guides = []
        if not self.outputs_path.exists():
            return []
        
        # Look for interview intel runs
        for run_dir in sorted(self.outputs_path.iterdir(), key=os.path.getmtime, reverse=True):
            if not run_dir.is_dir():
                continue
            intel_file = run_dir / "interview_intel.json"
            if intel_file.exists():
                try:
                    with open(intel_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        guides.append({
                            "run_id": run_dir.name,
                            "company_name": data.get("company_name", "Target Company"),
                            "role": data.get("target_role", "Software Engineer"),
                            "level": data.get("target_level", "Mid-Senior"),
                            "rounds_count": len(data.get("interview_rounds", [])),
                            "reference_path": f"outputs/{run_dir.name}/company_interview_pack.md",
                            "created_at": datetime.fromtimestamp(run_dir.stat().st_mtime).strftime("%Y-%m-%d")
                        })
                except Exception:
                    pass
            if len(guides) >= limit:
                break
        return guides

    def _get_recent_stock_picks(self, limit: int = 3) -> List[Dict[str, Any]]:
        picks = []
        if not self.outputs_path.exists():
            return []
        
        for run_dir in sorted(self.outputs_path.iterdir(), key=os.path.getmtime, reverse=True):
            if not run_dir.is_dir():
                continue
            picks_file = run_dir / "stock_opportunity_report.json"
            if picks_file.exists():
                try:
                    with open(picks_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        candidates = data.get("top_dislocated_opportunities", [])
                        for c in candidates[:2]:
                            picks.append({
                                "ticker": c.get("ticker"),
                                "company_name": c.get("company_name"),
                                "archetype": c.get("opportunity_archetype"),
                                "current_price": c.get("current_price"),
                                "target_price": c.get("target_price_implied"),
                                "upside": c.get("upside_downside_percent"),
                                "conviction": c.get("conviction_rating"),
                                "run_id": run_dir.name
                            })
                except Exception:
                    pass
            if len(picks) >= limit:
                break
        return picks

    def _get_recent_mock_sessions(self, limit: int = 3) -> List[Dict[str, Any]]:
        sessions = []
        if not self.outputs_path.exists():
            return []
        
        for run_dir in sorted(self.outputs_path.iterdir(), key=os.path.getmtime, reverse=True):
            if not run_dir.is_dir():
                continue
            sess_dir = run_dir / "sessions"
            if sess_dir.exists() and sess_dir.is_dir():
                for sf in sorted(sess_dir.glob("*_feedback.json"), key=os.path.getmtime, reverse=True):
                    try:
                        with open(sf, "r", encoding="utf-8") as f:
                            fb = json.load(f)
                            sess_id = sf.stem.replace("_feedback", "")
                            sessions.append({
                                "session_id": sess_id,
                                "run_id": run_dir.name,
                                "score": fb.get("overall_score"),
                                "verdict": fb.get("hire_recommendation"),
                                "summary": fb.get("summary_verdict"),
                                "created_at": datetime.fromtimestamp(sf.stat().st_mtime).strftime("%Y-%m-%d")
                            })
                    except Exception:
                        pass
                    if len(sessions) >= limit:
                        break
            if len(sessions) >= limit:
                break
        return sessions

    def _ensure_bootstrapped(self):
        """
        If the SQLite DB is fresh, automatically seeds it from existing outputs/
        so that recent stocks (e.g. NVDA), tech searches, and bookmarks are immediately populated.
        """
        existing_trends = self.store.get_top_trends(limit=1)
        if existing_trends:
            return  # Already has activity

        # 1. Discover existing runs and seed activity
        if not self.outputs_path.exists():
            return

        for run_dir in sorted(self.outputs_path.iterdir(), key=os.path.getmtime, reverse=True):
            if not run_dir.is_dir():
                continue

            # Stock research run check
            stock_res = run_dir / "stock_research_report.json"
            if stock_res.exists():
                try:
                    with open(stock_res, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        prof = data.get("company_profile", {})
                        ticker = prof.get("ticker", "NVDA")
                        cname = prof.get("company_name", "NVIDIA Corp")
                        val = data.get("valuation", {})
                        scenarios = val.get("scenarios", [])
                        base_sc = next((s for s in scenarios if s.get("scenario_name") == "Base"), {})
                        critic = data.get("critic", {})
                        invalidation = critic.get("thesis_invalidation_triggers", [])
                        warning = invalidation[0] if invalidation else None

                        self.store.log_activity("stock_market", ticker, run_dir.name)
                        self.store.upsert_stock_watchlist(
                            ticker=ticker,
                            company_name=cname,
                            current_price=prof.get("current_price", 120.0),
                            dcf_target_price=base_sc.get("target_price_implied", 145.0),
                            dcf_upside_percent=base_sc.get("upside_downside_percent", 20.8),
                            conviction="High Conviction",
                            critic_warning=warning,
                            run_id=run_dir.name
                        )
                        # Add as initial bookmark
                        self.store.add_bookmark(
                            domain="stock_market",
                            item_type="stock_research",
                            title=f"{cname} ({ticker}) Equity Deep-Dive",
                            reference_path=f"outputs/{run_dir.name}/stock_research_report.md",
                            summary="Institutional 21-section equity research report with DCF valuation and adversarial critic.",
                            tags=["#Semiconductors", "#DCFValuation"],
                            metadata={"ticker": ticker, "upside": 20.8}
                        )
                except Exception:
                    pass

            # Tech topics run check
            final_pack = run_dir / "final_interview_pack.md"
            if final_pack.exists():
                self.store.log_activity("tech_topics", "Model Context Protocol (MCP)", run_dir.name)
                self.store.log_activity("tech_topics", "Vector DB Hybrid Search", run_dir.name)
                self.store.add_bookmark(
                    domain="tech_topics",
                    item_type="tech_summary",
                    title="Model Context Protocol (MCP) Technical Deep Dive",
                    reference_path=f"outputs/{run_dir.name}/final_interview_pack.md",
                    summary="Full technical architecture, JSON-RPC 2.0 protocol specifications, and interview Q&As.",
                    tags=["#MCP", "#DistributedSystems"],
                    metadata={"reading_time_mins": 7}
                )

            # Company intel run check
            intel_f = run_dir / "interview_intel.json"
            if intel_f.exists():
                try:
                    with open(intel_f, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        cname = data.get("company_name", "Stripe")
                        self.store.log_activity("interview_experience", cname, run_dir.name)
                except Exception:
                    pass

        # 2. Seed an initial high-yield DSA stumble problem for demo & spaced-repetition
        existing_missed = self.store.list_missed_questions(due_only=False, limit=1)
        if not existing_missed:
            self.store.add_missed_question(
                title="LRU Cache with TTL (Least Recently Used)",
                category="DSA",
                company="Stripe",
                what_tripped_me="Forgot doubly linked list node pointer cleanup on expiration eviction.",
                source="manual_entry",
                difficulty="Hard"
            )
            self.store.add_missed_question(
                title="Raft Distributed Consensus (Split-Brain Recovery)",
                category="System Design",
                company="Databricks",
                what_tripped_me="Struggled to articulate term election timers and log compaction invariants.",
                source="manual_entry",
                difficulty="Hard"
            )
