from typing import Dict, Any, List
from research_agent.travel.state import TravelPlannerState
from research_agent.travel.benchmark_data import resolve_gateway_airport

# Canonical city sets for common country inputs
CANONICAL_COUNTRY_CITIES: Dict[str, List[str]] = {
    "japan": ["Tokyo", "Kyoto", "Osaka", "Nara"],
    "italy": ["Milan", "Florence", "Rome", "Venice"],
    "france": ["Paris", "Lyon", "Nice"],
    "switzerland": ["Zurich", "Lucerne", "Interlaken", "Geneva"],
    "germany": ["Frankfurt", "Munich", "Berlin"],
    "spain": ["Barcelona", "Madrid", "Seville"],
    "uk": ["London", "Oxford", "Edinburgh"],
    "united kingdom": ["London", "Bath", "Edinburgh"],
    "vietnam": ["Hanoi", "Da Nang", "Hoi An", "Ho Chi Minh City"],
    "thailand": ["Bangkok", "Chiang Mai", "Phuket"],
    "singapore": ["Singapore"],
    "uae": ["Dubai", "Abu Dhabi"],
    "dubai": ["Dubai", "Abu Dhabi"]
}

class GatewayAgent:
    """
    Identifies the most cost-effective gateway airport for flights from India
    and locks in the round-trip entry/exit hub.
    """

    def process(self, state: TravelPlannerState) -> Dict[str, Any]:
        input_params = state.get("input_params", {})
        destinations = input_params.get("destinations", ["Japan"])
        origin_city = input_params.get("origin_city", "Mumbai")

        # Resolve primary gateway airport
        gateway = resolve_gateway_airport(destinations)

        # Determine target cities list
        first_dest_lower = destinations[0].strip().lower() if destinations else "japan"
        
        target_cities: List[str] = []
        destination_country = gateway.country

        if first_dest_lower in CANONICAL_COUNTRY_CITIES:
            # User specified a country name
            target_cities = list(CANONICAL_COUNTRY_CITIES[first_dest_lower])
        else:
            # Check if any destination matches a country key
            matched = False
            for key, cities in CANONICAL_COUNTRY_CITIES.items():
                if key in first_dest_lower or any(key in d.lower() for d in destinations):
                    target_cities = list(cities)
                    destination_country = key.title()
                    matched = True
                    break
            
            if not matched:
                # User provided specific cities
                target_cities = [d.strip().title() for d in destinations]
        
        # Ensure the gateway airport city is the very first city in the sequence
        gateway_city = gateway.city.title()
        if gateway_city in target_cities:
            target_cities.remove(gateway_city)
        target_cities.insert(0, gateway_city)

        # Cap cities based on trip days (at least 2 days per city on average)
        trip_days = input_params.get("trip_days", 7)
        max_cities = max(1, trip_days // 2)
        target_cities = target_cities[:max_cities]

        return {
            "gateway_airport": gateway.model_dump(),
            "target_cities": target_cities,
            "destination_country": destination_country,
            "status": "gateway_resolved"
        }
