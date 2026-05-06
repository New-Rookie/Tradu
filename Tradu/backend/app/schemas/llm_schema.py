from __future__ import annotations

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, field_validator


TravelStyle = Literal["relaxed", "standard", "intensive"]
WalkingTolerance = Literal["low", "medium", "high"]
TransportPreference = Literal["walk", "public_transport", "taxi", "drive", "mixed"]
PoiType = Literal[
    "景点", "夜景", "餐饮", "商圈", "citywalk", "博物馆", "拍照点", "人文景点", "亲子", "酒店区域", "交通枢纽", "其他"
]
RecommendedTime = Literal["上午", "下午", "晚上", "全天", "不确定"]
Priority = Literal["hard_constraint", "soft_preference", "unknown"]
ActionType = Literal[
    "remove_poi", "replace_poi", "increase_preference", "decrease_preference",
    "decrease_walking", "decrease_budget", "increase_rest_time",
    "weather_adjustment", "regenerate_all", "unknown"
]
ToolName = Literal["search_poi", "calculate_route", "query_weather", "generate_itinerary", "explain_itinerary"]


class TravelIntent(BaseModel):
    destination: Optional[str] = None
    days: Optional[int] = Field(default=None, ge=1, le=30)
    budget: Optional[float] = Field(default=None, ge=0)
    preferences: List[str] = Field(default_factory=list)
    avoid: List[str] = Field(default_factory=list)
    travel_style: TravelStyle = "standard"
    walking_tolerance: WalkingTolerance = "medium"
    transport_preference: TransportPreference = "mixed"
    need_hotel_area: bool = True
    need_weather_adjustment: bool = True
    has_imported_note: bool = False
    missing_fields: List[str] = Field(default_factory=list)
    clarifying_question: str = ""

    @field_validator("preferences", "avoid", "missing_fields", mode="before")
    @classmethod
    def ensure_list(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return value


class ExtractedPoi(BaseModel):
    raw_name: str
    normalized_name: str
    poi_type: PoiType = "其他"
    tags: List[str] = Field(default_factory=list)
    recommended_time: RecommendedTime = "不确定"
    suggested_duration_minutes: Optional[int] = Field(default=None, ge=0, le=600)
    tips: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0, le=1)


class NoteExtractionResult(BaseModel):
    city: Optional[str] = None
    pois: List[ExtractedPoi] = Field(default_factory=list)
    global_tips: List[str] = Field(default_factory=list)
    detected_days: Optional[int] = Field(default=None, ge=1, le=30)


class DailyExplanation(BaseModel):
    day_index: int
    explanation: str
    tips: List[str] = Field(default_factory=list)


class ItineraryExplanation(BaseModel):
    summary: str
    daily_explanations: List[DailyExplanation] = Field(default_factory=list)
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    suitable_for: List[str] = Field(default_factory=list)


class RouteAdjustAction(BaseModel):
    action_type: ActionType
    target_poi: str = ""
    target_preference: str = ""
    reason: str = ""


class RouteAdjustIntent(BaseModel):
    actions: List[RouteAdjustAction] = Field(default_factory=list)
    priority: Priority = "unknown"
    need_regenerate: bool = True
    user_message: str = ""


class ToolCallSuggestion(BaseModel):
    tool_name: ToolName
    arguments: Dict[str, Any] = Field(default_factory=dict)
    reason: str = ""


class ToolDecisionResult(BaseModel):
    tool_calls: List[ToolCallSuggestion] = Field(default_factory=list)
