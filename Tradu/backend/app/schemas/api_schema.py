from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1)


class IntentParseRequest(BaseModel):
    text: str = Field(..., min_length=1)


class NoteExtractRequest(BaseModel):
    text: str = Field(..., min_length=1)


class RouteCalculateRequest(BaseModel):
    origin: str = Field(..., description="经纬度，格式：longitude,latitude")
    destination: str = Field(..., description="经纬度，格式：longitude,latitude")
    mode: str = Field("walking", description="walking / driving / transit")
    city: str = "重庆"


class ItineraryGenerateRequest(BaseModel):
    destination: str = "重庆"
    days: int = Field(1, ge=1, le=10)
    budget: Optional[float] = None
    preferences: List[str] = []
    avoid: List[str] = []
    travel_style: str = "standard"
    walking_tolerance: str = "medium"
    transport_preference: str = "public_transport"
    imported_pois: List[str] = []
    session_id: Optional[str] = None
    need_meal_planning: bool = True
    need_hotel_area: bool = True
    budget_control_level: str = "normal"
    budget_control: str = "normal"


class PoiItem(BaseModel):
    id: int
    poi_name: str
    city: str
    district: str = ""
    poi_type: str = ""
    tags: List[str] = []
    nearby_area: str = ""
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    amap_poi_id: str = ""
    match_status: str = ""


class DayRouteItem(BaseModel):
    sort_order: int
    poi_name: str
    poi_type: str = ""
    nearby_area: str = ""
    suggested_duration_minutes: int = 90
    reason: str = ""


class DayRoute(BaseModel):
    day_index: int
    title: str
    items: List[DayRouteItem]


class ItineraryPlan(BaseModel):
    plan_type: str
    title: str
    summary: str
    days: List[DayRoute]
    estimated_cost_low: float = 0
    estimated_cost_high: float = 0
    warnings: List[str] = []


class ItineraryGenerateResponse(BaseModel):
    itinerary_id: str
    destination: str
    plans: List[ItineraryPlan]


class LLMJsonResponse(BaseModel):
    raw: Dict[str, Any]

class SessionCreateRequest(BaseModel):
    session_id: Optional[str] = None


class ServicePoiRefreshRequest(BaseModel):
    city: str = "重庆"
    nearby_area: str
    service_types: List[str] = ["restaurant", "hotel"]


class ItineraryAdjustRequest(BaseModel):
    session_id: str
    instruction: str


class SessionOnlyRequest(BaseModel):
    session_id: str


class RemovePoiRequest(BaseModel):
    session_id: str
    poi_name: str


class CompressDayRequest(BaseModel):
    session_id: str
    day_index: int = Field(..., ge=1)


class ContinueFromLocationRequest(BaseModel):
    session_id: str
    longitude: float
    latitude: float
    current_time: Optional[str] = None
