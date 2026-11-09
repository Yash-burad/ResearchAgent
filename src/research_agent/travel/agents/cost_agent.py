from typing import Dict, Any
from research_agent.travel.state import TravelPlannerState
from research_agent.travel.models import CostBreakdown
from research_agent.travel.benchmark_data import (
    get_hotel_nightly_benchmark,
    get_daily_public_transit_benchmark,
    get_intercity_transit_leg_benchmark,
    get_daily_food_benchmark
)

class CostAgent:
    """
    Computes deterministic line-item costs for flights, hotels, public inter-city transit,
    intra-city transit, attraction tickets, and dining.
    Enforces the 1.2x budget constraint and penalizes every rupee over 1.0x budget.
    """

    def process(self, state: TravelPlannerState) -> Dict[str, Any]:
        input_params = state.get("input_params", {})
        target_budget = float(input_params.get("target_budget_inr", 150000.0))
        tier = input_params.get("travel_tier", "mid")
        travelers = int(input_params.get("travelers_count", 1))
        trip_days = int(input_params.get("trip_days", 7))
        gateway_airport = state.get("gateway_airport", {})
        destination_country = state.get("destination_country", "Japan")
        itinerary = state.get("current_itinerary", [])
        route_sequence = state.get("route_city_sequence", [])

        # 1. Flights
        base_flight_rate = float(gateway_airport.get("est_roundtrip_flight_inr_per_person", 45000.0))
        total_flights = base_flight_rate * travelers

        # 2. Accommodations (Total nights = trip_days - 1)
        nights = max(1, trip_days - 1)
        nightly_rate = get_hotel_nightly_benchmark(destination_country, tier)
        # Rooms needed: 1 room per 2 travelers
        rooms = max(1, (travelers + 1) // 2)
        total_accommodation = nights * nightly_rate * rooms

        # 3. Inter-city public transit
        # Count transitions between distinct cities
        unique_legs = max(0, len(route_sequence) - 1)
        intercity_leg_mode, intercity_leg_price = get_intercity_transit_leg_benchmark(destination_country, tier, distance_km=280.0)
        total_intercity = unique_legs * intercity_leg_price * travelers

        # 4. Intra-city public transit
        daily_intracity = get_daily_public_transit_benchmark(destination_country, tier)
        total_intracity = trip_days * daily_intracity * travelers

        # 5. Attraction tickets
        total_tickets_per_person = 0.0
        for day in itinerary:
            for act in day.get("activities", []):
                total_tickets_per_person += float(act.get("cost_inr", 0.0))
        total_attraction_tickets = total_tickets_per_person * travelers

        # 6. Food & incidentals
        daily_food = get_daily_food_benchmark(destination_country, tier)
        total_food = trip_days * daily_food * travelers

        # Total cost calculation
        total_cost = (
            total_flights
            + total_accommodation
            + total_intercity
            + total_intracity
            + total_attraction_tickets
            + total_food
        )

        budget_ratio = round(total_cost / max(1.0, target_budget), 3)
        # Penalize every rupee over target budget (1.0x)
        excess_ratio = max(0.0, (total_cost - target_budget) / max(1.0, target_budget))
        penalty_score = round(excess_ratio * 100.0, 1)
        is_within_cap = (budget_ratio <= 1.2)

        breakdown = CostBreakdown(
            international_flights_inr=round(total_flights, 2),
            accommodation_total_inr=round(total_accommodation, 2),
            intercity_transit_inr=round(total_intercity, 2),
            intracity_transit_inr=round(total_intracity, 2),
            attraction_tickets_inr=round(total_attraction_tickets, 2),
            food_and_incidentals_inr=round(total_food, 2),
            total_cost_inr=round(total_cost, 2),
            target_budget_inr=round(target_budget, 2),
            budget_ratio=budget_ratio,
            penalty_score=penalty_score,
            is_within_budget_cap=is_within_cap
        )

        return {
            "cost_breakdown": breakdown.model_dump(),
            "status": "cost_estimated"
        }
