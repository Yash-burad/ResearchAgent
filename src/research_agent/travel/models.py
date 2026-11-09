from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

TravelTier = Literal["budget", "mid", "luxury"]
PaceStyle = Literal["relaxed", "balanced", "fast_paced"]


class TravelPlannerInput(BaseModel):
    destinations: List[str] = Field(
        ...,
        description="List of target countries or cities (e.g. ['Japan'] or ['Tokyo', 'Kyoto', 'Osaka'])"
    )
    origin_city: str = Field(
        default="Mumbai",
        description="Departure hub in India (e.g., Mumbai, Delhi, Bengaluru, Chennai, Hyderabad)"
    )
    trip_days: int = Field(
        ...,
        ge=3,
        le=30,
        description="Total trip duration in days"
    )
    target_budget_inr: float = Field(
        ...,
        gt=10000,
        description="Target total trip budget in Indian Rupees (INR)"
    )
    travel_tier: TravelTier = Field(
        default="mid",
        description="Travel tier: budget (hostels/bus/walk), mid (3-4 star/metro/train), luxury (4-5 star/express rail/taxi)"
    )
    travelers_count: int = Field(
        default=1,
        ge=1,
        description="Number of travelers sharing rooms where applicable"
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Estimated start date (YYYY-MM-DD)"
    )
    pace_style: PaceStyle = Field(
        default="balanced",
        description="Travel pace preference: relaxed, balanced, fast_paced"
    )


class GatewayAirport(BaseModel):
    city: str
    airport_code: str
    airport_name: str
    country: str
    est_roundtrip_flight_inr_per_person: float
    direct_flight_available: bool = True
    notes: str = ""


class AttractionItem(BaseModel):
    id: str
    name: str
    city: str
    category: str = "Culture & Heritage"
    description: str
    avg_dwell_time_hours: float = 2.0
    ticket_cost_inr: float = 0.0
    opening_hours: Optional[str] = "09:00 - 18:00"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source_platform: Optional[str] = None  # e.g., "Tripoto", "Wanderlog", "Thrillophilia", "MakeMyTrip", "Lonely Planet"
    source_url: Optional[str] = None


class DayActivity(BaseModel):
    time_slot: str  # "Morning (09:00 - 12:30)", "Afternoon (14:00 - 17:30)", "Evening (18:30 - 21:30)"
    activity_name: str
    location: str
    description: str
    transit_mode: str  # e.g. "Metro Line 1 (15 min)", "Walk (8 min)", "Regional Train (30 min)"
    cost_inr: float = 0.0
    opening_hours: Optional[str] = None
    booking_advice: Optional[str] = None


class DaySchedule(BaseModel):
    day_number: int
    date: Optional[str] = None
    city: str
    theme: str
    activities: List[DayActivity] = Field(default_factory=list)
    day_transit_summary: str = ""
    hotel_recommendation: Optional[str] = None
    estimated_day_cost_inr: float = 0.0


class CostBreakdown(BaseModel):
    international_flights_inr: float
    accommodation_total_inr: float
    intercity_transit_inr: float
    intracity_transit_inr: float
    attraction_tickets_inr: float
    food_and_incidentals_inr: float
    total_cost_inr: float
    target_budget_inr: float
    budget_ratio: float  # total_cost / target_budget
    penalty_score: float = 0.0  # Max(0, (total - budget)/budget) * 100
    is_within_budget_cap: bool = True  # True if budget_ratio <= 1.2


class SideTripSuggestion(BaseModel):
    title: str
    base_city: str
    destination: str
    transit_duration_mins: int
    transit_mode: str  # "Local Train", "Public Express Bus"
    highlight: str
    estimated_add_on_cost_inr: float


class TravelItineraryResult(BaseModel):
    run_id: str
    title: str
    summary: str
    input_params: TravelPlannerInput
    gateway_airport: GatewayAirport
    route_city_sequence: List[str]
    days: List[DaySchedule]
    cost_breakdown: CostBreakdown
    satisfaction_score: float = 8.5
    satisfaction_verdict: str = "High Satisfaction"
    side_trips: List[SideTripSuggestion] = Field(default_factory=list)
    sourced_references: List[Dict[str, str]] = Field(default_factory=list)
    full_markdown_report: str = ""
