from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict


class TravelPlannerState(TypedDict, total=False):
    run_id: str
    input_params: Dict[str, Any]
    destination_country: str
    target_cities: List[str]
    gateway_airport: Optional[Dict[str, Any]]
    discovered_attractions: List[Dict[str, Any]]
    route_city_sequence: List[str]
    current_itinerary: List[Dict[str, Any]]
    cost_breakdown: Optional[Dict[str, Any]]
    satisfaction_score: float
    satisfaction_verdict: str
    satisfaction_feedback: List[str]
    side_trips: List[Dict[str, Any]]
    iteration_count: int
    pruning_directives: List[str]
    status: str
    errors: List[str]
    sourced_references: List[Dict[str, str]]
    final_result: Optional[Dict[str, Any]]
    final_markdown_report: str
