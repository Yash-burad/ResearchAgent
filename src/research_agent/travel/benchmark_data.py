"""
Benchmark tables for international gateway airports, flight price baselines from India,
tier-based hotel costs, and public transit fare estimations.
"""

from typing import Dict, Any, Tuple, Optional
from research_agent.travel.models import GatewayAirport, TravelTier

# Major gateway international airports mapped by country/region
GATEWAY_AIRPORTS_CATALOG: Dict[str, GatewayAirport] = {
    # Japan
    "japan": GatewayAirport(
        city="Tokyo",
        airport_code="NRT",
        airport_name="Narita International Airport",
        country="Japan",
        est_roundtrip_flight_inr_per_person=46000.0,
        direct_flight_available=True,
        notes="Primary intercontinental gateway; fast Narita Express rail connection to Tokyo central."
    ),
    "tokyo": GatewayAirport(
        city="Tokyo",
        airport_code="HND",
        airport_name="Haneda International Airport",
        country="Japan",
        est_roundtrip_flight_inr_per_person=48000.0,
        direct_flight_available=True,
        notes="Closest to downtown Tokyo (Monorail/Keikyu line link)."
    ),
    # Italy
    "italy": GatewayAirport(
        city="Milan",
        airport_code="MXP",
        airport_name="Milan Malpensa Airport",
        country="Italy",
        est_roundtrip_flight_inr_per_person=48000.0,
        direct_flight_available=True,
        notes="Most economical northern entry hub into Italy; Malpensa Express train directly to Milano Centrale."
    ),
    "rome": GatewayAirport(
        city="Rome",
        airport_code="FCO",
        airport_name="Leonardo da Vinci–Fiumicino Airport",
        country="Italy",
        est_roundtrip_flight_inr_per_person=51000.0,
        direct_flight_available=True,
        notes="Central Italy hub; Leonardo Express non-stop rail to Roma Termini."
    ),
    # France
    "france": GatewayAirport(
        city="Paris",
        airport_code="CDG",
        airport_name="Charles de Gaulle Airport",
        country="France",
        est_roundtrip_flight_inr_per_person=52000.0,
        direct_flight_available=True,
        notes="Direct Air India / Air France link from Delhi & Mumbai; RER B train to central Paris."
    ),
    "paris": GatewayAirport(
        city="Paris",
        airport_code="CDG",
        airport_name="Charles de Gaulle Airport",
        country="France",
        est_roundtrip_flight_inr_per_person=52000.0,
        direct_flight_available=True,
        notes="Main gateway to Western Europe rail network."
    ),
    # Switzerland
    "switzerland": GatewayAirport(
        city="Zurich",
        airport_code="ZRH",
        airport_name="Zurich Airport",
        country="Switzerland",
        est_roundtrip_flight_inr_per_person=56000.0,
        direct_flight_available=True,
        notes="Swiss rail station integrated under terminal; trains leave for all cantons every 10 mins."
    ),
    # Germany
    "germany": GatewayAirport(
        city="Frankfurt",
        airport_code="FRA",
        airport_name="Frankfurt Airport",
        country="Germany",
        est_roundtrip_flight_inr_per_person=49000.0,
        direct_flight_available=True,
        notes="High-speed ICE train station attached directly to Terminal 1."
    ),
    # Spain
    "spain": GatewayAirport(
        city="Barcelona",
        airport_code="BCN",
        airport_name="Josep Tarradellas Barcelona-El Prat",
        country="Spain",
        est_roundtrip_flight_inr_per_person=51000.0,
        direct_flight_available=False,
        notes="Aerobus or R2 Nord train directly into Plaça de Catalunya."
    ),
    # United Kingdom
    "united kingdom": GatewayAirport(
        city="London",
        airport_code="LHR",
        airport_name="London Heathrow Airport",
        country="United Kingdom",
        est_roundtrip_flight_inr_per_person=55000.0,
        direct_flight_available=True,
        notes="Piccadilly line and Elizabeth line provide direct tube access to central London."
    ),
    "uk": GatewayAirport(
        city="London",
        airport_code="LHR",
        airport_name="London Heathrow Airport",
        country="United Kingdom",
        est_roundtrip_flight_inr_per_person=55000.0,
        direct_flight_available=True,
        notes="Heathrow Express or Elizabeth Line directly into Paddington."
    ),
    # Vietnam
    "vietnam": GatewayAirport(
        city="Hanoi",
        airport_code="HAN",
        airport_name="Noi Bai International Airport",
        country="Vietnam",
        est_roundtrip_flight_inr_per_person=21000.0,
        direct_flight_available=True,
        notes="Direct VietJet / Vietnam Airlines flights from India; public Bus 86 connects to Old Quarter."
    ),
    # Thailand
    "thailand": GatewayAirport(
        city="Bangkok",
        airport_code="BKK",
        airport_name="Suvarnabhumi Airport",
        country="Thailand",
        est_roundtrip_flight_inr_per_person=19000.0,
        direct_flight_available=True,
        notes="Airport Rail Link connects to BTS Skytrain in 25 minutes for 45 THB."
    ),
    # Singapore
    "singapore": GatewayAirport(
        city="Singapore",
        airport_code="SIN",
        airport_name="Singapore Changi Airport",
        country="Singapore",
        est_roundtrip_flight_inr_per_person=23000.0,
        direct_flight_available=True,
        notes="Seamless MRT connection from Terminals 2 & 3."
    ),
    # United Arab Emirates
    "uae": GatewayAirport(
        city="Dubai",
        airport_code="DXB",
        airport_name="Dubai International Airport",
        country="United Arab Emirates",
        est_roundtrip_flight_inr_per_person=21000.0,
        direct_flight_available=True,
        notes="Red Line Metro connects terminals directly to Downtown Dubai."
    ),
    "dubai": GatewayAirport(
        city="Dubai",
        airport_code="DXB",
        airport_name="Dubai International Airport",
        country="United Arab Emirates",
        est_roundtrip_flight_inr_per_person=21000.0,
        direct_flight_available=True,
        notes="Frequent 3.5 hour direct flights from all major Indian metros."
    )
}

# Regional cost tiering coefficients
HIGH_COST_REGIONS = {"japan", "tokyo", "kyoto", "osaka", "switzerland", "zurich", "geneva", "uk", "london", "france", "paris", "germany", "italy", "usa", "australia", "singapore"}

def resolve_gateway_airport(destinations: list[str]) -> GatewayAirport:
    """
    Finds the most cost-effective gateway airport for the given destination list.
    Defaults to a reasonable international fallback if unlisted.
    """
    for dest in destinations:
        clean = dest.strip().lower()
        if clean in GATEWAY_AIRPORTS_CATALOG:
            return GATEWAY_AIRPORTS_CATALOG[clean]
        for key, port in GATEWAY_AIRPORTS_CATALOG.items():
            if key in clean or clean in key:
                return port

    # Generic Western Europe / Global fallback
    first_dest = destinations[0].strip().title() if destinations else "Destination"
    return GatewayAirport(
        city=first_dest,
        airport_code="INTL",
        airport_name=f"{first_dest} International Airport",
        country=first_dest,
        est_roundtrip_flight_inr_per_person=45000.0,
        direct_flight_available=False,
        notes="Scheduled round-trip hub from India."
    )

def get_hotel_nightly_benchmark(destination: str, tier: TravelTier) -> float:
    """
    Returns benchmark accommodation cost in INR per room/night based on regional costs and tier.
    """
    is_high_cost = any(h in destination.lower() for h in HIGH_COST_REGIONS)
    
    if is_high_cost:
        rates = {
            "budget": 3200.0,   # Well-reviewed hostel pod / guesthouse
            "mid": 7800.0,      # Quality 3-star / boutique private hotel
            "luxury": 24000.0   # 4.5 to 5-star premier hotel
        }
    else:
        rates = {
            "budget": 1600.0,   # Budget clean room / hostel
            "mid": 4500.0,      # High-rated 3/4-star hotel
            "luxury": 14000.0   # 5-star resort / luxury suite
        }
    return rates.get(tier, rates["mid"])

def get_daily_public_transit_benchmark(destination: str, tier: TravelTier) -> float:
    """
    Benchmark intra-city public transit spend per person/day in INR.
    Strictly public transit (walking + bus/metro) with occasional metered taxi allowance for mid/luxury.
    """
    is_high_cost = any(h in destination.lower() for h in HIGH_COST_REGIONS)
    base = 650.0 if is_high_cost else 350.0
    
    if tier == "budget":
        return base * 1.0       # Metro day pass / bus tickets + walking
    elif tier == "mid":
        return base * 1.8       # Metro pass + occasional local taxi ride for late-night/luggage
    else: # luxury
        return base * 4.5       # Unlimited metro pass + frequent local metered taxis

def get_intercity_transit_leg_benchmark(destination: str, tier: TravelTier, distance_km: float = 250.0) -> Tuple[str, float]:
    """
    Estimates public inter-city transit mode and price per person for a leg.
    Returns (mode_description, cost_inr).
    """
    is_high_cost = any(h in destination.lower() for h in HIGH_COST_REGIONS)
    
    if distance_km > 600:
        # Distance exceeds efficient rail -> budget commercial flight or long-distance sleeper rail
        if is_high_cost:
            return "Scheduled Inter-City Rail (Sleeper/Day) or Budget Flight", 7500.0 if tier != "luxury" else 12500.0
        else:
            return "Domestic Commercial Flight / Express Rail", 3800.0 if tier != "luxury" else 7500.0
    
    # Distance <= 600km -> High-speed or regional rail / coach
    if tier == "budget":
        cost = (distance_km * 7.5) if is_high_cost else (distance_km * 4.0)
        return "Public Regional Train / Long-Distance Coach (FlixBus)", max(1200.0, cost)
    elif tier == "mid":
        cost = (distance_km * 14.0) if is_high_cost else (distance_km * 7.0)
        return "Standard High-Speed Rail (2nd Class)", max(2400.0, cost)
    else: # luxury
        cost = (distance_km * 25.0) if is_high_cost else (distance_km * 12.0)
        return "Express High-Speed Rail (1st Class)", max(4500.0, cost)

def get_daily_food_benchmark(destination: str, tier: TravelTier) -> float:
    """
    Benchmark food and beverage per person/day in INR.
    """
    is_high_cost = any(h in destination.lower() for h in HIGH_COST_REGIONS)
    multiplier = 1.6 if is_high_cost else 1.0
    
    rates = {
        "budget": 1400.0 * multiplier,  # Street food, markets, casual noodles/delis
        "mid": 3200.0 * multiplier,     # Sit-down local trattorias, bistros, cafes
        "luxury": 7500.0 * multiplier   # High-end dining, multi-course experiences
    }
    return rates.get(tier, rates["mid"])
