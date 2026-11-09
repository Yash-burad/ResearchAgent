from typing import Literal
from langgraph.graph import StateGraph, START, END

from research_agent.travel.state import TravelPlannerState
from research_agent.travel.agents.gateway_agent import GatewayAgent
from research_agent.travel.agents.discovery_agent import DiscoveryAgent
from research_agent.travel.agents.cluster_tsp_agent import ClusterTSPAgent
from research_agent.travel.agents.itinerary_agent import ItineraryAgent
from research_agent.travel.agents.cost_agent import CostAgent
from research_agent.travel.agents.negotiator_agent import BudgetNegotiatorAgent
from research_agent.travel.agents.satisfaction_agent import SatisfactionAgent
from research_agent.travel.agents.suggestion_agent import SuggestionAgent
from research_agent.travel.agents.compiler_agent import CompilerAgent

# Initialize agents
gateway_agent = GatewayAgent()
discovery_agent = DiscoveryAgent()
cluster_tsp_agent = ClusterTSPAgent()
itinerary_agent = ItineraryAgent()
cost_agent = CostAgent()
negotiator_agent = BudgetNegotiatorAgent()
satisfaction_agent = SatisfactionAgent()
suggestion_agent = SuggestionAgent()
compiler_agent = CompilerAgent()

def node_gateway(state: TravelPlannerState):
    return gateway_agent.process(state)

def node_discovery(state: TravelPlannerState):
    return discovery_agent.process(state)

def node_cluster_tsp(state: TravelPlannerState):
    return cluster_tsp_agent.process(state)

def node_itinerary(state: TravelPlannerState):
    return itinerary_agent.process(state)

def node_cost(state: TravelPlannerState):
    return cost_agent.process(state)

def node_negotiator(state: TravelPlannerState):
    return negotiator_agent.process(state)

def node_satisfaction(state: TravelPlannerState):
    return satisfaction_agent.process(state)

def node_suggestion(state: TravelPlannerState):
    return suggestion_agent.process(state)

def node_compiler(state: TravelPlannerState):
    return compiler_agent.process(state)

def check_budget_condition(state: TravelPlannerState) -> Literal["negotiate", "satisfaction"]:
    cost_data = state.get("cost_breakdown", {})
    is_within_cap = cost_data.get("is_within_budget_cap", True)
    iteration_count = state.get("iteration_count", 0)

    # If exceeding 1.2x budget and we haven't hit loop limit (max 3 loops), negotiate down
    if not is_within_cap and iteration_count < 3:
        return "negotiate"
    return "satisfaction"

def check_satisfaction_condition(state: TravelPlannerState) -> Literal["negotiate", "suggestion"]:
    score = state.get("satisfaction_score", 8.0)
    iteration_count = state.get("iteration_count", 0)
    cost_data = state.get("cost_breakdown", {})
    budget_ratio = cost_data.get("budget_ratio", 1.0)

    # If satisfaction is poor (< 7.0) due to severe budget squeeze and iteration_count < 2, re-balance
    if score < 7.0 and budget_ratio > 1.2 and iteration_count < 2:
        return "negotiate"
    return "suggestion"

def create_travel_graph():
    """
    Constructs the LangGraph state machine for the autonomous multi-agent travel planner.
    """
    workflow = StateGraph(TravelPlannerState)

    # Register Nodes
    workflow.add_node("gateway_resolver", node_gateway)
    workflow.add_node("discovery", node_discovery)
    workflow.add_node("cluster_tsp", node_cluster_tsp)
    workflow.add_node("itinerary_generator", node_itinerary)
    workflow.add_node("cost_estimator", node_cost)
    workflow.add_node("budget_negotiator", node_negotiator)
    workflow.add_node("satisfaction_reviewer", node_satisfaction)
    workflow.add_node("suggestion_generator", node_suggestion)
    workflow.add_node("compiler", node_compiler)

    # Edges
    workflow.add_edge(START, "gateway_resolver")
    workflow.add_edge("gateway_resolver", "discovery")
    workflow.add_edge("discovery", "cluster_tsp")
    workflow.add_edge("cluster_tsp", "itinerary_generator")
    workflow.add_edge("itinerary_generator", "cost_estimator")

    # Conditional Budget Check
    workflow.add_conditional_edges(
        "cost_estimator",
        check_budget_condition,
        {
            "negotiate": "budget_negotiator",
            "satisfaction": "satisfaction_reviewer"
        }
    )

    # Budget Negotiator loops back into Itinerary Generator
    workflow.add_edge("budget_negotiator", "itinerary_generator")

    # Conditional Satisfaction Check
    workflow.add_conditional_edges(
        "satisfaction_reviewer",
        check_satisfaction_condition,
        {
            "negotiate": "budget_negotiator",
            "suggestion": "suggestion_generator"
        }
    )

    workflow.add_edge("suggestion_generator", "compiler")
    workflow.add_edge("compiler", END)

    return workflow.compile()
