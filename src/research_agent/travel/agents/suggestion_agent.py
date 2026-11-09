from typing import Dict, Any, List
from research_agent.travel.state import TravelPlannerState
from research_agent.travel.models import SideTripSuggestion

KNOWN_SIDE_TRIPS: Dict[str, List[SideTripSuggestion]] = {
    "Tokyo": [
        SideTripSuggestion(
            title="Kamakura Coastal Shrines & Great Buddha",
            base_city="Tokyo",
            destination="Kamakura",
            transit_duration_mins=55,
            transit_mode="JR Yokosuka Line Train",
            highlight="13-meter bronze Kotoku-in Buddha, bamboo groves at Hokoku-ji, and Enoden seaside tram.",
            estimated_add_on_cost_inr=1800.0
        ),
        SideTripSuggestion(
            title="Yokohama Bayside & Chinatown",
            base_city="Tokyo",
            destination="Yokohama",
            transit_duration_mins=28,
            transit_mode="JR Tokaido Line",
            highlight="Historic red brick warehouses, Minato Mirai skyline, and Japan's largest Chinatown.",
            estimated_add_on_cost_inr=900.0
        )
    ],
    "Kyoto": [
        SideTripSuggestion(
            title="Nara Deer Park & Todai-ji Giant Temple",
            base_city="Kyoto",
            destination="Nara",
            transit_duration_mins=45,
            transit_mode="JR Nara Line Rapid Train",
            highlight="Free-roaming sacred sika deer and the world's largest bronze Buddha statue at Todai-ji.",
            estimated_add_on_cost_inr=1400.0
        ),
        SideTripSuggestion(
            title="Uji Green Tea Capital & Byodoin Temple",
            base_city="Kyoto",
            destination="Uji",
            transit_duration_mins=20,
            transit_mode="JR Nara Line",
            highlight="Authentic ceremonial matcha tastings and the iconic Phoenix Hall featured on the 10-yen coin.",
            estimated_add_on_cost_inr=850.0
        )
    ],
    "Milan": [
        SideTripSuggestion(
            title="Lake Como & Varenna Lakeside Promenade",
            base_city="Milan",
            destination="Lake Como",
            transit_duration_mins=55,
            transit_mode="Trenord Regional Train to Varenna-Esino",
            highlight="Cobblestone alleys, dramatic Alpine fjord vistas, and scenic public ferry to Bellagio.",
            estimated_add_on_cost_inr=2200.0
        ),
        SideTripSuggestion(
            title="Bergamo Alta Medieval Walled Citadel",
            base_city="Milan",
            destination="Bergamo",
            transit_duration_mins=48,
            transit_mode="Regional Public Rail + Funicular",
            highlight="UNESCO Venetian walls, Piazza Vecchia, and panoramic funicular railway ride.",
            estimated_add_on_cost_inr=1200.0
        )
    ],
    "Florence": [
        SideTripSuggestion(
            title="Lucca Renaissance Walls & Piazza dell'Anfiteatro",
            base_city="Florence",
            destination="Lucca",
            transit_duration_mins=50,
            transit_mode="Regionale Train",
            highlight="Cycling atop 16th-century tree-lined defensive ramparts and Roman amphitheater square.",
            estimated_add_on_cost_inr=1400.0
        ),
        SideTripSuggestion(
            title="Pisa Miracle Square & Leaning Tower",
            base_city="Florence",
            destination="Pisa",
            transit_duration_mins=48,
            transit_mode="Regionale Veloce Rail",
            highlight="Iconic marble campanile and Romanesque cathedral in Campo dei Miracoli.",
            estimated_add_on_cost_inr=1900.0
        )
    ],
    "Rome": [
        SideTripSuggestion(
            title="Tivoli Villa d'Este Renaissance Fountains",
            base_city="Rome",
            destination="Tivoli",
            transit_duration_mins=45,
            transit_mode="Trenitalia Regional Rail",
            highlight="Hundreds of hydraulic Renaissance gravity fountains and lush UNESCO gardens.",
            estimated_add_on_cost_inr=1600.0
        )
    ],
    "Paris": [
        SideTripSuggestion(
            title="Palace of Versailles & Royal Gardens",
            base_city="Paris",
            destination="Versailles",
            transit_duration_mins=40,
            transit_mode="RER C Commuter Rail",
            highlight="Hall of Mirrors, Grand Trianon, and 800 hectares of classical French fountains.",
            estimated_add_on_cost_inr=2800.0
        )
    ]
}

class SuggestionAgent:
    """
    Identifies high-value nearby modular day-trips reachable via < 60 min public transit
    from the scheduled base cities, offering optional extensions without disrupting the core schedule.
    """

    def process(self, state: TravelPlannerState) -> Dict[str, Any]:
        target_cities = state.get("target_cities", [])
        gateway_airport = state.get("gateway_airport", {})
        gateway_city = gateway_airport.get("city", "Tokyo")

        suggestions: List[Dict[str, Any]] = []
        considered_cities = list(target_cities)
        if gateway_city not in considered_cities:
            considered_cities.append(gateway_city)

        for city in considered_cities:
            city_norm = city.strip().title()
            if city_norm in KNOWN_SIDE_TRIPS:
                for trip in KNOWN_SIDE_TRIPS[city_norm]:
                    suggestions.append(trip.model_dump())

        # Generic fallback if no specific catalog match
        if not suggestions:
            first_city = target_cities[0] if target_cities else gateway_city
            suggestions.append(SideTripSuggestion(
                title=f"{first_city} Countryside & Historic Village Excursion",
                base_city=first_city,
                destination=f"Greater {first_city} Region",
                transit_duration_mins=45,
                transit_mode="Local Public Train / Bus",
                highlight=f"Scenic regional landscapes and heritage village accessible on a half-day public transit pass.",
                estimated_add_on_cost_inr=1500.0
            ).model_dump())

        return {
            "side_trips": suggestions[:3],
            "status": "side_trips_suggested"
        }
