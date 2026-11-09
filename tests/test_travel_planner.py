import time
import pytest
from research_agent.travel.models import TravelPlannerInput
from research_agent.travel.benchmark_data import (
    resolve_gateway_airport,
    get_hotel_nightly_benchmark,
    get_daily_public_transit_benchmark
)
from research_agent.travel.agents.gateway_agent import GatewayAgent
from research_agent.travel.agents.cluster_tsp_agent import ClusterTSPAgent
from research_agent.travel.agents.cost_agent import CostAgent
from research_agent.travel.graph import create_travel_graph
from research_agent.travel.service import TravelPlannerService

def test_gateway_resolver():
    gateway = resolve_gateway_airport(["Japan"])
    assert gateway.airport_code in ["NRT", "HND"]
    assert gateway.city == "Tokyo"
    assert gateway.country == "Japan"
    assert gateway.est_roundtrip_flight_inr_per_person > 0

    gateway_italy = resolve_gateway_airport(["Italy", "Rome"])
    assert gateway_italy.city in ["Milan", "Rome"]

def test_gateway_agent_state():
    agent = GatewayAgent()
    state = {
        "input_params": {
            "destinations": ["Japan"],
            "origin_city": "Mumbai",
            "trip_days": 7
        }
    }
    res = agent.process(state)
    assert res["gateway_airport"]["city"] == "Tokyo"
    assert res["target_cities"][0] == "Tokyo"
    assert len(res["target_cities"]) >= 2

def test_cluster_tsp_circular_loop():
    agent = ClusterTSPAgent()
    state = {
        "gateway_airport": {"city": "Tokyo"},
        "target_cities": ["Tokyo", "Kyoto", "Osaka"],
        "input_params": {"trip_days": 8}
    }
    res = agent.process(state)
    route = res["route_city_sequence"]
    assert route[0] == "Tokyo"
    assert route[-1] == "Tokyo"
    assert "Kyoto" in route
    assert "Osaka" in route

def test_cost_agent_penalty_calculation():
    agent = CostAgent()
    state = {
        "input_params": {
            "target_budget_inr": 100000.0,
            "travel_tier": "budget",
            "travelers_count": 1,
            "trip_days": 5
        },
        "gateway_airport": {
            "city": "Tokyo",
            "est_roundtrip_flight_inr_per_person": 46000.0
        },
        "destination_country": "Japan",
        "route_city_sequence": ["Tokyo", "Tokyo"],
        "current_itinerary": [
            {"activities": [{"cost_inr": 500.0}]}
        ]
    }
    res = agent.process(state)
    cost = res["cost_breakdown"]
    assert cost["international_flights_inr"] == 46000.0
    assert cost["total_cost_inr"] > 0
    assert "penalty_score" in cost
    assert "is_within_budget_cap" in cost

def test_end_to_end_travel_graph():
    graph = create_travel_graph()
    initial_state = {
        "run_id": "test_travel_run_01",
        "input_params": {
            "destinations": ["Japan"],
            "origin_city": "Mumbai",
            "trip_days": 7,
            "target_budget_inr": 160000.0,
            "travel_tier": "mid",
            "travelers_count": 1,
            "pace_style": "balanced"
        },
        "iteration_count": 0,
        "pruning_directives": [],
        "errors": []
    }
    final_state = graph.invoke(initial_state)
    
    assert final_state["status"] == "completed"
    assert "final_result" in final_state
    result = final_state["final_result"]
    assert len(result["days"]) == 7
    assert result["gateway_airport"]["city"] == "Tokyo"
    assert result["cost_breakdown"]["total_cost_inr"] > 0
    assert len(result["side_trips"]) > 0
    assert "final_markdown_report" in final_state
    assert "# 7-Day Japan Master Travel Itinerary" in final_state["final_markdown_report"]

def test_travel_planner_service(tmp_path):
    service = TravelPlannerService(outputs_dir=tmp_path)
    input_data = TravelPlannerInput(
        destinations=["Italy"],
        origin_city="Delhi",
        trip_days=6,
        target_budget_inr=180000.0,
        travel_tier="mid"
    )
    run_id = service.start_plan_run(input_data)
    assert run_id.startswith("travel_run_")

    # Poll for completion (runs locally in < 3s)
    max_wait = 10
    start = time.time()
    while time.time() - start < max_wait:
        plan = service.get_plan(run_id)
        if plan and plan.get("status") in ["completed", "failed"]:
            break
        time.sleep(0.5)

    plan = service.get_plan(run_id)
    assert plan is not None
    assert plan["status"] == "completed"
    assert plan["result"] is not None
    assert len(plan["result"]["days"]) == 6
