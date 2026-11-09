from typing import Dict, Any, List
from research_agent.travel.state import TravelPlannerState

class SatisfactionAgent:
    """
    Evaluates the human traveler experience, pacing balance, and sight coverage.
    Ensures that aggressive cost-cutting does not turn the trip into an exhausting or barebones ordeal.
    """

    def process(self, state: TravelPlannerState) -> Dict[str, Any]:
        itinerary = state.get("current_itinerary", [])
        cost_breakdown = state.get("cost_breakdown", {})
        input_params = state.get("input_params", {})
        trip_days = int(input_params.get("trip_days", 7))
        target_cities = state.get("target_cities", [])
        budget_ratio = cost_breakdown.get("budget_ratio", 1.0)
        penalty_score = cost_breakdown.get("penalty_score", 0.0)

        feedback: List[str] = []
        score = 8.8

        # 1. Pacing & Fatigue Check
        city_count = len(target_cities)
        if city_count > 1 and (trip_days / city_count) < 1.8:
            score -= 1.2
            feedback.append("Fast pacing warning: Less than 2 nights per base city may cause travel fatigue.")
        else:
            score += 0.4
            feedback.append("Excellent pacing: Balanced stay durations allow deep cultural immersion without daily packing.")

        # 2. Daily Activity Density Check
        total_activities = sum(len(d.get("activities", [])) for d in itinerary)
        avg_act_per_day = total_activities / max(1, trip_days)
        if avg_act_per_day < 2.0:
            score -= 1.0
            feedback.append("Low activity density: Schedule has sparse exploration blocks.")
        elif avg_act_per_day > 4.0:
            score -= 0.8
            feedback.append("Overpacked days: More than 4 major activities daily risks schedule slippage.")
        else:
            feedback.append("Optimal daily density: 2-3 structured highlights per day with built-in rest buffers.")

        # 3. Budget Alignment Check
        if budget_ratio > 1.2:
            score -= 2.0
            feedback.append(f"Budget exceeded by {int((budget_ratio - 1.0)*100)}%: Cost pruning mandatory.")
        elif budget_ratio > 1.0:
            score -= (penalty_score / 25.0)
            feedback.append(f"Minor budget overflow ({int(penalty_score)}% penalty applied), but within acceptable 1.2x threshold.")
        else:
            score += 0.5
            feedback.append("Budget discipline: Fully funded within 1.0x baseline budget target.")

        final_score = max(1.0, min(10.0, round(score, 1)))
        
        if final_score >= 8.5:
            verdict = "Outstanding Experience & Value"
        elif final_score >= 7.5:
            verdict = "Solid & Realistic Pacing"
        else:
            verdict = "Sub-Optimal Pacing or Budget Tension"

        return {
            "satisfaction_score": final_score,
            "satisfaction_verdict": verdict,
            "satisfaction_feedback": feedback,
            "status": "satisfaction_evaluated"
        }
