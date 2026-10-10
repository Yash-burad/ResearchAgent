import os
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from research_agent.models import TopicCandidate, RefinedTopic, ResearchNotes, TopicSummary

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_OUTPUTS_PATH = PROJECT_ROOT / "outputs"

class RunStore:
    DEFAULT_OUTPUTS_DIR: str = str(DEFAULT_OUTPUTS_PATH)

    def __init__(self, outputs_dir: Optional[str] = None):
        target_dir = outputs_dir or self.DEFAULT_OUTPUTS_DIR
        self.outputs_path = Path(target_dir).resolve()
        self.outputs_dir = self.outputs_path
        self.outputs_path.mkdir(exist_ok=True, parents=True)
        self.run_id: str = ""
        self.run_path: Path = Path()
        self.research_path: Path = Path()
        self.summaries_path: Path = Path()
        self.games_path: Path = Path()
        self.sessions_path: Path = Path()

    def create_run(self, run_id: Optional[str] = None) -> str:
        """
        Creates a new run folder with subfolders.
        """
        if not run_id:
            run_id = f"run_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}"
        self.run_id = run_id
        self.run_path = self.outputs_path / run_id
        self.research_path = self.run_path / "research"
        self.summaries_path = self.run_path / "summaries"
        self.games_path = self.run_path / "games"
        self.sessions_path = self.run_path / "sessions"

        self.run_path.mkdir(exist_ok=True, parents=True)
        self.research_path.mkdir(exist_ok=True, parents=True)
        self.summaries_path.mkdir(exist_ok=True, parents=True)
        self.games_path.mkdir(exist_ok=True, parents=True)
        self.sessions_path.mkdir(exist_ok=True, parents=True)
        return self.run_id

    def set_run(self, run_id: str):
        """
        Sets store to point to an existing run folder.
        """
        self.run_id = run_id
        self.run_path = self.outputs_path / run_id
        self.research_path = self.run_path / "research"
        self.summaries_path = self.run_path / "summaries"
        self.games_path = self.run_path / "games"
        self.sessions_path = self.run_path / "sessions"
        self.games_path.mkdir(exist_ok=True, parents=True)
        self.sessions_path.mkdir(exist_ok=True, parents=True)


    def write_json(self, filename: str, data: Any):
        """
        Writes data (dict or list) as JSON to the run directory.
        """
        if not self.run_path or self.run_path == Path():
            self.create_run()
        file_path = self.run_path / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def read_json(self, filename: str) -> Any:
        """
        Reads JSON data from the run directory.
        """
        if not self.run_path or self.run_path == Path():
            return None
        file_path = self.run_path / filename
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_trending_topics(self, topics: List[TopicCandidate]):
        data = [t.model_dump() for t in topics]
        self.write_json("trending_topics.json", data)

    def save_refined_topics(self, topics: List[RefinedTopic]):
        data = [t.model_dump() for t in topics]
        self.write_json("refined_topics.json", data)

    def save_research_notes(self, topic_filename: str, notes: ResearchNotes):
        if not self.research_path or self.research_path == Path():
            self.create_run()
        file_path = self.research_path / f"{topic_filename}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(notes.model_dump(), f, indent=2, ensure_ascii=False)

    def save_summary(self, topic_filename: str, summary: TopicSummary):
        if not self.summaries_path or self.summaries_path == Path():
            self.create_run()
        file_path = self.summaries_path / f"{topic_filename}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(summary.model_dump(), f, indent=2, ensure_ascii=False)

    def save_game(self, topic_slug: str, game_type: str, game_data: Any):
        if not self.games_path or self.games_path == Path():
            self.create_run(self.run_id if self.run_id else None)
        self.games_path.mkdir(exist_ok=True, parents=True)
        file_path = self.games_path / f"{topic_slug}_{game_type}.json"
        dumped = game_data.model_dump() if hasattr(game_data, "model_dump") else game_data
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(dumped, f, indent=2, ensure_ascii=False)

    def load_game(self, topic_slug: str, game_type: str) -> Optional[Dict[str, Any]]:
        if not self.games_path or self.games_path == Path():
            return None
        file_path = self.games_path / f"{topic_slug}_{game_type}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_games(self) -> List[Dict[str, str]]:
        if not self.games_path or not self.games_path.exists():
            return []
        games = []
        for file in self.games_path.glob("*.json"):
            name = file.stem
            parts = name.rsplit("_", 1)
            if len(parts) == 2:
                games.append({"topic_slug": parts[0], "game_type": parts[1], "filename": file.name})
        return games

    def save_interview_intel(self, intel: Any):
        dumped = intel.model_dump() if hasattr(intel, "model_dump") else intel
        self.write_json("interview_intel.json", dumped)
        
        # Save markdown pack
        md_content = dumped.get("prep_pack_markdown", "")
        if md_content and self.run_path:
            md_file = self.run_path / "company_interview_pack.md"
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(md_content)

    def load_interview_intel(self) -> Optional[Dict[str, Any]]:
        return self.read_json("interview_intel.json")

    def save_session(self, session: Any):
        if not self.sessions_path or self.sessions_path == Path():
            self.create_run(self.run_id if self.run_id else None)
        self.sessions_path.mkdir(exist_ok=True, parents=True)
        dumped = session.model_dump() if hasattr(session, "model_dump") else session
        session_id = dumped.get("session_id", "session_default")
        file_path = self.sessions_path / f"{session_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(dumped, f, indent=2, ensure_ascii=False)

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        if not self.sessions_path or not self.sessions_path.exists():
            return None
        file_path = self.sessions_path / f"{session_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_sessions(self) -> List[Dict[str, Any]]:
        if not self.sessions_path or not self.sessions_path.exists():
            return []
        sessions = []
        for file in sorted(self.sessions_path.glob("*.json"), key=os.path.getmtime, reverse=True):
            if file.stem.endswith("_feedback"):
                continue
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sessions.append({
                        "session_id": data.get("session_id"),
                        "round_name": data.get("round_name"),
                        "round_type": data.get("round_type"),
                        "company_name": data.get("company_name"),
                        "status": data.get("status"),
                        "created_at": data.get("created_at"),
                        "message_count": len(data.get("messages", []))
                    })
            except Exception:
                pass
        return sessions

    def save_feedback(self, session_id: str, feedback: Any):
        if not self.sessions_path or self.sessions_path == Path():
            self.create_run(self.run_id if self.run_id else None)
        self.sessions_path.mkdir(exist_ok=True, parents=True)
        dumped = feedback.model_dump() if hasattr(feedback, "model_dump") else feedback
        file_path = self.sessions_path / f"{session_id}_feedback.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(dumped, f, indent=2, ensure_ascii=False)

    def load_feedback(self, session_id: str) -> Optional[Dict[str, Any]]:
        if not self.sessions_path or not self.sessions_path.exists():
            return None
        file_path = self.sessions_path / f"{session_id}_feedback.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_stock_research(self, report: Any):
        dumped = report.model_dump() if hasattr(report, "model_dump") else report
        self.write_json("stock_research_report.json", dumped)

    def load_stock_research(self) -> Optional[Dict[str, Any]]:
        return self.read_json("stock_research_report.json")

    def save_stock_picks(self, report: Any):
        dumped = report.model_dump() if hasattr(report, "model_dump") else report
        self.write_json("stock_opportunity_report.json", dumped)

    def load_stock_picks(self) -> Optional[Dict[str, Any]]:
        return self.read_json("stock_opportunity_report.json")


