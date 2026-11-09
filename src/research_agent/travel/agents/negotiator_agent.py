from typing import Dict, Any, List
from research_agent.travel.state import TravelPlannerState

class BudgetNegotiatorAgent:
    """
    Enforces the 1.2x budget constraint by executing a prioritized pruning hierarchy:
    1. Downgrade hotel tier
    2. Swap express trains for regional/coach
    3. Prune paid secondary attraction tickets
    4. Drop the most distant outlier city
    """

    def process(self, state: TravelPlannerState) -> Dict[str, Any]:
        cost_data = state.get("cost_breakdown", {})
        budget_ratio = cost_data.get("budget_ratio", 1.0)
        input_params = dict(state.get("input_params", {}))
        current_tier = input_params.get("travel_tier", "mid")
        iteration_count = state.get("iteration_count", 0) + 1
        target_cities = list(state.get("target_cities", []))
        directives: List[str] = list(state.get("pruning_directives", []))

        # Apply Step 1: Downgrade Tier if possible
        if current_tier == "luxury":
            input_params["travel_tier"] = "mid"
            directives.append("Downgraded accommodation from Luxury to Mid-tier (3-4 Star boutique).")
        elif current_tier == "mid" and budget_ratio > 1.2:
            input_params["travel_tier"] = "budget"
            directives.append("Downscaled accommodation to Budget/Guesthouse tier to meet target budget.")

        # Apply Step 2: Transit optimization
        directives.append("Swapped premium high-speed rail to standard regional public rail and local city passes.")

        # Apply Step 3: Trim paid attractions
        directives.append("Replaced premium guided museum entries with public viewpoints, historic squares, and gardens.")

        # Apply Step 4: Drop outlier city if severely over budget and more than 1 city
        if budget_ratio > 1.35 and len(target_cities) > 2:
            dropped = target_cities.pop()
            directives.append(f"Pruned outlier destination '{dropped}' to eliminate long inter-city rail costs and hotel overhead.")

        return {
            "input_params": input_params,
            "target_cities": target_cities,
            "pruning_directives": directives,
            "iteration_count": iteration_count,
            "status": "budget_pruning_applied"
        }
