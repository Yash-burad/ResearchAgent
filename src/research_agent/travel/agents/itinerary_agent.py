from typing import Dict, Any, List
from research_agent.travel.state import TravelPlannerState
from research_agent.travel.models import DaySchedule, DayActivity

HOTEL_RECOMMENDATIONS = {
    "Tokyo": {
        "budget": "UNPLAN Shinjuku or Wise Owl Hostels (Clean pod/capsule, ₹3,200/night)",
        "mid": "Hotel Gracery Shinjuku or Candeo Hotels Roppongi (3-4 Star, central metro access, ₹7,800/night)",
        "luxury": "Park Hyatt Tokyo or Palace Hotel Tokyo (5-Star luxury overlooking Imperial Gardens, ₹26,000/night)"
    },
    "Kyoto": {
        "budget": "Piece Hostel Sanjo or Comic & Capsule Hotel (₹3,000/night)",
        "mid": "The Thousand Kyoto or Cross Hotel Kyoto (Near Kawaramachi, ₹7,500/night)",
        "luxury": "The Ritz-Carlton Kyoto or Hoshinoya Kyoto (₹28,000/night)"
    },
    "Osaka": {
        "budget": "Hotel The Rock Capsule or J-Hoppers (₹2,800/night)",
        "mid": "Cross Hotel Osaka (Right off Dotonbori Canal, ₹7,200/night)",
        "luxury": "Conrad Osaka or Swissotel Nankai (₹24,000/night)"
    },
    "Milan": {
        "budget": "Ostello Bello Grande (Right beside Milano Centrale station, ₹3,500/night)",
        "mid": "Ibis Milano Centro or Starhotels Echo (₹8,200/night)",
        "luxury": "Armani Hotel Milano or Mandarin Oriental (₹32,000/night)"
    },
    "Florence": {
        "budget": "PLUS Florence (Hostel with pool & terrace, ₹3,200/night)",
        "mid": "Hotel Pendini or c-hotels Ambasciatori (₹7,900/night)",
        "luxury": "Four Seasons Hotel Firenze or Portrait Firenze (₹30,000/night)"
    },
    "Rome": {
        "budget": "The YellowSquare Rome (Near Termini Station, ₹3,400/night)",
        "mid": "Hotel Artemide or iQ Hotel Roma (₹8,500/night)",
        "luxury": "Hotel de Russie or Hassler Roma (₹34,000/night)"
    }
}

class ItineraryAgent:
    """
    Synthesizes the master day-by-day, hour-by-hour operational schedule with
    deterministic morning/afternoon/evening blocks, public transit instructions,
    and tier-calibrated accommodation.
    """

    def process(self, state: TravelPlannerState) -> Dict[str, Any]:
        input_params = state.get("input_params", {})
        trip_days = input_params.get("trip_days", 7)
        tier = input_params.get("travel_tier", "mid")
        route_sequence = state.get("route_city_sequence", ["Tokyo", "Tokyo"])
        discovered_attractions = state.get("discovered_attractions", [])
        gateway_airport = state.get("gateway_airport", {})
        gateway_city = gateway_airport.get("city", "Tokyo")
        pruning_directives = state.get("pruning_directives", [])

        # Index attractions by city
        city_attractions_map: Dict[str, List[Dict[str, Any]]] = {}
        for att in discovered_attractions:
            c = att.get("city", gateway_city)
            if c not in city_attractions_map:
                city_attractions_map[c] = []
            city_attractions_map[c].append(att)

        # Build schedule days
        # Distribute intermediate cities across days 2 to N-1
        days: List[DaySchedule] = []
        unique_cities = route_sequence[:-1]
        
        # Determine active city for each day
        day_to_city: List[str] = []
        if len(unique_cities) == 1:
            day_to_city = [unique_cities[0]] * trip_days
        else:
            # Multi-city distribution
            days_per_city = max(1, (trip_days - 1) // len(unique_cities))
            for i, city in enumerate(unique_cities):
                count = days_per_city if i < len(unique_cities) - 1 else (trip_days - 1 - days_per_city * (len(unique_cities) - 1))
                for _ in range(max(1, count)):
                    day_to_city.append(city)
            while len(day_to_city) < trip_days - 1:
                day_to_city.append(unique_cities[-1])
            # Last day returns to gateway airport city
            day_to_city.append(gateway_city)

        # Generate each day
        current_city = gateway_city
        for day_num in range(1, trip_days + 1):
            target_city = day_to_city[day_num - 1]
            is_city_change = (target_city != current_city and day_num > 1)
            is_first_day = (day_num == 1)
            is_last_day = (day_num == trip_days)
            current_city = target_city

            activities: List[DayActivity] = []
            hotel_rec = HOTEL_RECOMMENDATIONS.get(target_city, {}).get(
                tier, f"Standard {tier.title()} Hotel in {target_city} Central"
            )

            if is_first_day:
                theme = f"Arrival in {gateway_city} & Historic Orientation"
                transit_summary = f"Arrival at {gateway_airport.get('airport_name', 'Airport')}. Public Airport Express train directly into {gateway_city} central."
                activities.append(DayActivity(
                    time_slot="Morning (10:00 - 13:00)",
                    activity_name=f"Landing & Airport Express to {gateway_city}",
                    location=gateway_airport.get("airport_name", "International Airport"),
                    description="Immigration, baggage retrieval, and airport express train to central hotel.",
                    transit_mode="Airport Express Train (45 min)",
                    cost_inr=1200.0 if tier != "luxury" else 2400.0,
                    booking_advice="Purchase ticket at automated station kiosks or tap IC/contactless card."
                ))
                activities.append(DayActivity(
                    time_slot="Afternoon (14:00 - 16:30)",
                    activity_name="Hotel Check-in & Neighborhood Walking Orientation",
                    location=f"Central {gateway_city}",
                    description=f"Drop luggage at {hotel_rec.split('(')[0].strip()}, grab quick local lunch, and stretch legs.",
                    transit_mode="Walk (10 min)",
                    cost_inr=0.0
                ))
                # First available attraction for evening
                first_att = city_attractions_map.get(gateway_city, [None])[0]
                activities.append(DayActivity(
                    time_slot="Evening (17:30 - 21:00)",
                    activity_name=first_att["name"] if first_att else f"{gateway_city} Old Town Sunset Walk",
                    location=first_att["city"] if first_att else gateway_city,
                    description=first_att["description"] if first_att else "Atmospheric evening stroll through illuminated heritage alleyways.",
                    transit_mode="Public Metro / Walk (15 min)",
                    cost_inr=first_att["ticket_cost_inr"] if first_att else 0.0,
                    opening_hours=first_att["opening_hours"] if first_att else "Open 24 hours"
                ))

            elif is_last_day:
                theme = f"Return to {gateway_city} & Flight Departure to India"
                transit_summary = f"Public airport express train from {target_city} to {gateway_airport.get('airport_code')} Airport for homebound flight."
                activities.append(DayActivity(
                    time_slot="Morning (09:00 - 12:00)",
                    activity_name="Last Souvenir Shopping & Local Bakery Breakfast",
                    location=f"{target_city} Central Market",
                    description="Pick up local treats, crafts, and tax-free souvenirs before hotel checkout.",
                    transit_mode="Walk (10 min)",
                    cost_inr=0.0
                ))
                activities.append(DayActivity(
                    time_slot="Afternoon (13:30 - 17:00)",
                    activity_name=f"Airport Transit to {gateway_airport.get('airport_name')}",
                    location=gateway_airport.get("airport_name"),
                    description="Board public airport express line, check bags, clear immigration and duty-free.",
                    transit_mode="Airport Express Line / Metro (50 min)",
                    cost_inr=1200.0,
                    booking_advice="Arrive at international departure terminal 3 hours before flight."
                ))

            else:
                # Regular exploration day
                attractions_for_city = city_attractions_map.get(target_city, [])
                att_index = (day_num * 2) % max(1, len(attractions_for_city))
                morning_att = attractions_for_city[att_index] if attractions_for_city else None
                afternoon_att = attractions_for_city[(att_index + 1) % len(attractions_for_city)] if attractions_for_city else None

                if is_city_change:
                    theme = f"Public High-Speed Transit to {target_city} & City Exploration"
                    transit_summary = f"High-speed public rail from {day_to_city[day_num - 2]} to {target_city}."
                    activities.append(DayActivity(
                        time_slot="Morning (08:30 - 11:30)",
                        activity_name=f"High-Speed Public Train: {day_to_city[day_num - 2]} to {target_city}",
                        location=f"{target_city} Central Station",
                        description=f"Board 2nd class high-speed rail. Enjoy scenic window views across countryside.",
                        transit_mode=f"High-Speed Public Train (2h 10m)",
                        cost_inr=2800.0 if tier != "luxury" else 4800.0,
                        booking_advice="Reserve seat on official national railway app in advance."
                    ))
                else:
                    theme = f"Deep Dive into {target_city} Cultural Icons"
                    transit_summary = f"Intra-city public metro passes and walking."
                    activities.append(DayActivity(
                        time_slot="Morning (09:00 - 12:30)",
                        activity_name=morning_att["name"] if morning_att else f"{target_city} Heritage District",
                        location=target_city,
                        description=morning_att["description"] if morning_att else "Cultural architecture and morning garden walks.",
                        transit_mode="Public Metro (15 min)",
                        cost_inr=morning_att["ticket_cost_inr"] if morning_att else 0.0,
                        opening_hours=morning_att["opening_hours"] if morning_att else "09:00 - 17:00"
                    ))

                activities.append(DayActivity(
                    time_slot="Afternoon (14:00 - 17:30)",
                    activity_name=afternoon_att["name"] if afternoon_att else f"{target_city} Panorama & Arts",
                    location=target_city,
                    description=afternoon_att["description"] if afternoon_att else "Iconic viewpoint and cultural exhibits.",
                    transit_mode="Public Bus / Metro (12 min)",
                    cost_inr=afternoon_att["ticket_cost_inr"] if afternoon_att else 0.0,
                    opening_hours=afternoon_att["opening_hours"] if afternoon_att else "10:00 - 18:00"
                ))

                activities.append(DayActivity(
                    time_slot="Evening (18:30 - 21:30)",
                    activity_name=f"{target_city} Night Market & Local Culinary Exploration",
                    location=f"{target_city} Food Street",
                    description="Casual dining, street food treats, and illuminated evening walking trails.",
                    transit_mode="Walk (10 min)",
                    cost_inr=0.0
                ))

            # Calculate day ticket costs
            day_ticket_cost = sum(act.cost_inr for act in activities)

            days.append(DaySchedule(
                day_number=day_num,
                city=target_city,
                theme=theme,
                activities=activities,
                day_transit_summary=transit_summary,
                hotel_recommendation=hotel_rec,
                estimated_day_cost_inr=day_ticket_cost
            ))

        return {
            "current_itinerary": [d.model_dump() for d in days],
            "status": "itinerary_synthesized"
        }
