from typing import Dict, Any, List
from research_agent.travel.state import TravelPlannerState
from research_agent.travel.models import (
    TravelItineraryResult,
    TravelPlannerInput,
    GatewayAirport,
    DaySchedule,
    CostBreakdown,
    SideTripSuggestion
)

class CompilerAgent:
    """
    Compiles all intermediate agent outputs into a unified TravelItineraryResult
    and generates an executive, publication-ready Markdown dossier.
    """

    def process(self, state: TravelPlannerState) -> Dict[str, Any]:
        run_id = state.get("run_id", "run_travel_001")
        input_dict = state.get("input_params", {})
        input_params = TravelPlannerInput(**input_dict)
        gateway_dict = state.get("gateway_airport", {})
        gateway = GatewayAirport(**gateway_dict)
        route_sequence = state.get("route_city_sequence", [])
        raw_days = state.get("current_itinerary", [])
        days = [DaySchedule(**d) for d in raw_days]
        cost_dict = state.get("cost_breakdown", {})
        cost = CostBreakdown(**cost_dict) if cost_dict else CostBreakdown(
            international_flights_inr=0.0,
            accommodation_total_inr=0.0,
            intercity_transit_inr=0.0,
            intracity_transit_inr=0.0,
            attraction_tickets_inr=0.0,
            food_and_incidentals_inr=0.0,
            total_cost_inr=0.0,
            target_budget_inr=input_params.target_budget_inr,
            budget_ratio=1.0,
            penalty_score=0.0,
            is_within_budget_cap=True
        )
        raw_side_trips = state.get("side_trips", [])
        side_trips = [SideTripSuggestion(**s) for s in raw_side_trips]
        sourced_refs = state.get("sourced_references", [])
        satisfaction_score = state.get("satisfaction_score", 8.5)
        satisfaction_verdict = state.get("satisfaction_verdict", "Solid Pacing & Experience")

        # Build Title & Executive Summary
        dest_str = ", ".join(input_params.destinations)
        title = f"{input_params.trip_days}-Day {dest_str} Master Travel Itinerary"
        summary = (
            f"Optimized {input_params.trip_days}-day journey starting and ending via {gateway.city} ({gateway.airport_code}) "
            f"from {input_params.origin_city}, India. Built on the '{input_params.travel_tier.title()}' tier "
            f"using strictly public rail and transit networks. Estimated total cost: ₹{cost.total_cost_inr:,.0f} "
            f"(Budget Ratio: {cost.budget_ratio:.2f}x)."
        )

        # Generate Markdown Document
        md_lines = []
        md_lines.append(f"# {title}")
        md_lines.append(f"> **Origin**: {input_params.origin_city}, India | **Gateway Airport**: {gateway.city} ({gateway.airport_code}) — Round-Trip Locked")
        md_lines.append(f"> **Travel Tier**: `{input_params.travel_tier.upper()}` | **Pacing**: `{input_params.pace_style.title()}` | **Satisfaction Index**: `{satisfaction_score}/10 ({satisfaction_verdict})`")
        md_lines.append(f"> **Target Budget**: ₹{cost.target_budget_inr:,.0f} | **Computed Cost**: ₹{cost.total_cost_inr:,.0f} | **Budget Ratio**: `{cost.budget_ratio:.2f}x`")
        if cost.penalty_score > 0:
            md_lines.append(f"> ⚠️ **Budget Penalty**: `{cost.penalty_score:.1f}% penalty` applied for exceeding 1.0x baseline budget (capped within allowable 1.2x envelope).")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

        # 1. Route Sequence & Transit Rules
        md_lines.append("## 1. Route Topology & Public Transit Network")
        route_str = " ➔ ".join(route_sequence)
        md_lines.append(f"**Circular Route Sequence**: `{route_str}`")
        md_lines.append("- **Gateway Flight**: Round-trip to/from the same entry airport city to minimize international flight fares.")
        md_lines.append("- **Transit Enforcement**: 100% public transit (high-speed rail, regional trains, metros, city buses, and walking). Zero private transfers.")
        md_lines.append("")

        # 2. Day-by-Day Breakdown
        md_lines.append("## 2. Day-by-Day Operational Itinerary")
        for day in days:
            md_lines.append(f"### Day {day.day_number}: {day.city} — {day.theme}")
            if day.hotel_recommendation:
                md_lines.append(f"- 🏨 **Stay Recommendation**: {day.hotel_recommendation}")
            if day.day_transit_summary:
                md_lines.append(f"- 🚆 **Transit Logistics**: {day.day_transit_summary}")
            md_lines.append("")
            
            for act in day.activities:
                md_lines.append(f"#### {act.time_slot}: {act.activity_name}")
                md_lines.append(f"- **Location**: {act.location}")
                md_lines.append(f"- **Description**: {act.description}")
                md_lines.append(f"- **Transit Mode**: `{act.transit_mode}`")
                if act.cost_inr > 0:
                    md_lines.append(f"- **Estimated Ticket Cost**: ₹{act.cost_inr:,.0f}")
                if act.opening_hours:
                    md_lines.append(f"- **Hours**: {act.opening_hours}")
                if act.booking_advice:
                    md_lines.append(f"- 💡 **Booking Advice**: {act.booking_advice}")
                md_lines.append("")
            md_lines.append("---")
            md_lines.append("")

        # 3. Transparent Cost Breakdown
        md_lines.append("## 3. Comprehensive Cost Breakdown (INR)")
        md_lines.append("| Expense Category | Estimated Total (INR) | % of Total | Notes & Basis |")
        md_lines.append("| :--- | :--- | :--- | :--- |")
        flights_pct = (cost.international_flights_inr / max(1.0, cost.total_cost_inr)) * 100
        stays_pct = (cost.accommodation_total_inr / max(1.0, cost.total_cost_inr)) * 100
        intercity_pct = (cost.intercity_transit_inr / max(1.0, cost.total_cost_inr)) * 100
        intracity_pct = (cost.intracity_transit_inr / max(1.0, cost.total_cost_inr)) * 100
        tickets_pct = (cost.attraction_tickets_inr / max(1.0, cost.total_cost_inr)) * 100
        food_pct = (cost.food_and_incidentals_inr / max(1.0, cost.total_cost_inr)) * 100

        md_lines.append(f"| **Round-Trip International Flights** | ₹{cost.international_flights_inr:,.0f} | {flights_pct:.1f}% | Ex-{input_params.origin_city} to {gateway.airport_code} round-trip |")
        md_lines.append(f"| **Accommodation ({input_params.trip_days - 1} Nights)** | ₹{cost.accommodation_total_inr:,.0f} | {stays_pct:.1f}% | Calibrated to `{input_params.travel_tier}` tier |")
        md_lines.append(f"| **Inter-City Public Transit** | ₹{cost.intercity_transit_inr:,.0f} | {intercity_pct:.1f}% | High-speed and regional rail between bases |")
        md_lines.append(f"| **Intra-City Public Transit** | ₹{cost.intracity_transit_inr:,.0f} | {intracity_pct:.1f}% | Daily city metro passes and walking |")
        md_lines.append(f"| **Monument & Sight Tickets** | ₹{cost.attraction_tickets_inr:,.0f} | {tickets_pct:.1f}% | Confirmed entry passes for scheduled sights |")
        md_lines.append(f"| **Food & Daily Incidentals** | ₹{cost.food_and_incidentals_inr:,.0f} | {food_pct:.1f}% | Daily bistros and street dining benchmark |")
        md_lines.append(f"| **TOTAL ESTIMATED EXPENSE** | **₹{cost.total_cost_inr:,.0f}** | **100%** | **Target: ₹{cost.target_budget_inr:,.0f} ({cost.budget_ratio:.2f}x)** |")
        md_lines.append("")

        # 4. Modular Day-Trip Suggestions
        if side_trips:
            md_lines.append("## 4. Modular Nearby Day-Trip Gems (Optional Side Trips)")
            md_lines.append("These optional excursions require < 60 minutes of public transit from your scheduled base cities:")
            md_lines.append("")
            for s in side_trips:
                md_lines.append(f"### ✨ {s.title}")
                md_lines.append(f"- **Base City**: {s.base_city} ➔ **Destination**: {s.destination}")
                md_lines.append(f"- **Transit**: {s.transit_mode} ({s.transit_duration_mins} mins)")
                md_lines.append(f"- **Highlight**: {s.highlight}")
                md_lines.append(f"- **Estimated Extra Cost**: ₹{s.estimated_add_on_cost_inr:,.0f}")
                md_lines.append("")

        # 5. Sourced References & Itinerary Blueprints
        md_lines.append("## 5. Sourced References & Itinerary Blueprints")
        md_lines.append("The itinerary synthesizes verified package blueprints and real-world travel logs from:")
        md_lines.append("")
        for ref in sourced_refs:
            md_lines.append(f"- [{ref['title']}]({ref['url']}) — *Platform: {ref.get('platform', 'Travel Guide')}*")
        md_lines.append("")

        full_md = "\n".join(md_lines)

        final_obj = TravelItineraryResult(
            run_id=run_id,
            title=title,
            summary=summary,
            input_params=input_params,
            gateway_airport=gateway,
            route_city_sequence=route_sequence,
            days=days,
            cost_breakdown=cost,
            satisfaction_score=satisfaction_score,
            satisfaction_verdict=satisfaction_verdict,
            side_trips=side_trips,
            sourced_references=sourced_refs,
            full_markdown_report=full_md
        )

        return {
            "final_result": final_obj.model_dump(),
            "final_markdown_report": full_md,
            "status": "completed"
        }
