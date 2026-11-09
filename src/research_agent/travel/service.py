import json
import os
import uuid
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from research_agent.travel.models import TravelPlannerInput
from research_agent.travel.graph import create_travel_graph

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

class TravelPlannerService:
    """
    Service layer to execute, track, and persist multi-agent travel plans.
    """

    def __init__(self, outputs_dir: Optional[Path] = None):
        self.outputs_dir = outputs_dir or OUTPUTS_DIR
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.runs: Dict[str, Dict[str, Any]] = {}
        self.graph = create_travel_graph()
        self._load_existing_runs()

    def _load_existing_runs(self):
        """Scans outputs directory for previous travel plan runs."""
        if not self.outputs_dir.exists():
            return
        for run_folder in self.outputs_dir.iterdir():
            if run_folder.is_dir() and run_folder.name.startswith("travel_run_"):
                res_file = run_folder / "travel_itinerary.json"
                if res_file.exists():
                    try:
                        with open(res_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            self.runs[run_folder.name] = {
                                "run_id": run_folder.name,
                                "status": "completed",
                                "result": data,
                                "created_at": datetime.fromtimestamp(run_folder.stat().st_mtime).isoformat()
                            }
                    except Exception:
                        pass

    def start_plan_run(self, input_params: TravelPlannerInput) -> str:
        """
        Starts a travel plan run in a background worker thread and returns the run_id immediately.
        """
        run_id = f"travel_run_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}_{uuid.uuid4().hex[:4]}"
        
        self.runs[run_id] = {
            "run_id": run_id,
            "status": "processing",
            "progress_message": "Initializing Gateway Airport Resolver...",
            "input_params": input_params.model_dump(),
            "created_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }

        # Spawn background execution
        worker = threading.Thread(target=self._execute_pipeline, args=(run_id, input_params))
        worker.daemon = True
        worker.start()

        return run_id

    def _execute_pipeline(self, run_id: str, input_params: TravelPlannerInput):
        try:
            initial_state = {
                "run_id": run_id,
                "input_params": input_params.model_dump(),
                "iteration_count": 0,
                "pruning_directives": [],
                "errors": []
            }

            self.runs[run_id]["progress_message"] = "Resolving Gateway Hub & Mining Travel Itineraries..."
            final_state = self.graph.invoke(initial_state)

            final_result = final_state.get("final_result")
            final_markdown = final_state.get("final_markdown_report", "")

            # Persist to disk
            run_dir = self.outputs_dir / run_id
            run_dir.mkdir(parents=True, exist_ok=True)

            with open(run_dir / "travel_itinerary.json", "w", encoding="utf-8") as f:
                json.dump(final_result, f, indent=2, ensure_ascii=False)

            with open(run_dir / "travel_itinerary.md", "w", encoding="utf-8") as f:
                f.write(final_markdown)

            self.runs[run_id]["status"] = "completed"
            self.runs[run_id]["progress_message"] = "Master Itinerary Complete"
            self.runs[run_id]["result"] = final_result
            self.runs[run_id]["markdown_path"] = str(run_dir / "travel_itinerary.md")

        except Exception as e:
            self.runs[run_id]["status"] = "failed"
            self.runs[run_id]["error"] = str(e)
            self.runs[run_id]["progress_message"] = f"Failed: {str(e)}"

    def get_plan(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self.runs.get(run_id)

    def list_plans(self) -> List[Dict[str, Any]]:
        return sorted(
            list(self.runs.values()),
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
