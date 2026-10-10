from typing import Dict, Any

# In-memory database to store agent execution status, progress, and results.
# Structure per run_id:
# {
#     "status": "discovering" | "pending_selection" | "researching" | "summarizing" | "completed" | "failed",
#     "progress": int (0-100),
#     "current_step": str,
#     "interests": str,
#     "raw_topics": list,
#     "refined_topics": list,
#     "selected_topics": list,
#     "final_pack": str (markdown),
#     "error": str
# }
RUNS_DB: Dict[str, Dict[str, Any]] = {}
