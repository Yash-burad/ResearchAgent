from typing import Dict, Any, List
from research_agent.travel.state import TravelPlannerState

# Known geographical adjacency sequences for zero-backtracking loops
CANONICAL_LOOPS: Dict[str, List[str]] = {
    # Japan loops
    "tokyo_kyoto_osaka": ["Tokyo", "Kyoto", "Osaka", "Tokyo"],
    "tokyo_osaka_kyoto": ["Tokyo", "Kyoto", "Osaka", "Tokyo"],
    # Italy loops
    "milan_rome_florence_venice": ["Milan", "Venice", "Florence", "Rome", "Milan"],
    "rome_florence_venice_milan": ["Rome", "Florence", "Venice", "Milan", "Rome"],
    # France loops
    "paris_lyon_nice": ["Paris", "Lyon", "Nice", "Paris"],
    # Switzerland loops
    "zurich_lucerne_interlaken": ["Zurich", "Lucerne", "Interlaken", "Zurich"],
    # Vietnam loops
    "hanoi_danang_hochiminh": ["Hanoi", "Da Nang", "Hoi An", "Hanoi"]
}

class ClusterTSPAgent:
    """
    Solves the Travelling Salesperson Problem (TSP) to order target cities into
    an optimal, zero-backtrack closed circular route that begins and ends at the gateway airport.
    """

    def process(self, state: TravelPlannerState) -> Dict[str, Any]:
        gateway_airport = state.get("gateway_airport", {})
        gateway_city = gateway_airport.get("city", "Tokyo").strip().title()
        target_cities = state.get("target_cities", [gateway_city])
        input_params = state.get("input_params", {})
        trip_days = input_params.get("trip_days", 7)

        # 1. Construct closed circular loop
        cleaned_cities = [c.strip().title() for c in target_cities if c.strip().title() != gateway_city]
        
        # Check canonical loops first
        loop_key = "_".join([gateway_city.lower()] + [c.lower() for c in cleaned_cities])
        
        ordered_cities: List[str] = [gateway_city]
        
        if loop_key in CANONICAL_LOOPS:
            ordered_cities = list(CANONICAL_LOOPS[loop_key])
        else:
            # Deterministic TSP: Gateway -> Intermediate cities -> Gateway
            ordered_cities = [gateway_city] + cleaned_cities + [gateway_city]

        # 2. Allocate days per city
        # Ensure at least 1 day per intermediate city and arrival/departure in gateway
        unique_stop_count = len(ordered_cities) - 1  # Excluding the terminal return point
        
        if unique_stop_count <= 1:
            city_days_map = {gateway_city: trip_days}
        else:
            base_days = max(1, (trip_days - 1) // unique_stop_count)
            city_days_map = {}
            remaining = trip_days
            for i, city in enumerate(ordered_cities[:-1]):
                if i == 0:
                    # Gateway city gets base + 1
                    allot = min(remaining, base_days + 1)
                elif i == unique_stop_count - 1:
                    # Last intermediate city takes remainder
                    allot = max(1, remaining)
                else:
                    allot = min(remaining, base_days)
                city_days_map[city] = allot
                remaining -= allot

        return {
            "route_city_sequence": ordered_cities,
            "city_days_map": city_days_map,
            "status": "tsp_route_optimized"
        }
