from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.base_mixins import TimestampMixin


class Itinerary(Base, TimestampMixin):
    __tablename__ = "itineraries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    guide_import_id: Mapped[int | None] = mapped_column(ForeignKey("guide_imports.id"), index=True, nullable=True)
    destination: Mapped[str] = mapped_column(String(64), nullable=False)
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    budget: Mapped[int | None] = mapped_column(Integer, nullable=True)
    preferences: Mapped[list | None] = mapped_column(JSON, nullable=True)
    avoid_preferences: Mapped[list | None] = mapped_column(JSON, nullable=True)
    travel_style: Mapped[str] = mapped_column(String(32), default="standard", nullable=False)
    walking_tolerance: Mapped[str] = mapped_column(String(32), default="medium", nullable=False)
    transport_preference: Mapped[str] = mapped_column(String(32), default="mixed", nullable=False)
    raw_user_input: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_intent: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="itineraries")
    guide_import = relationship("GuideImport")
    plans = relationship("ItineraryPlan", back_populates="itinerary")


class ItineraryPlan(Base, TimestampMixin):
    __tablename__ = "itinerary_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    itinerary_id: Mapped[int] = mapped_column(ForeignKey("itineraries.id"), index=True, nullable=False)
    plan_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    suitable_for: Mapped[list | None] = mapped_column(JSON, nullable=True)
    advantages: Mapped[list | None] = mapped_column(JSON, nullable=True)
    disadvantages: Mapped[list | None] = mapped_column(JSON, nullable=True)
    total_estimated_cost_low: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_estimated_cost_high: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_transport_time_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_walking_distance_meters: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_selected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    itinerary = relationship("Itinerary", back_populates="plans")
    daily_routes = relationship("DailyRoute", back_populates="plan")


class DailyRoute(Base, TimestampMixin):
    __tablename__ = "daily_routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("itinerary_plans.id"), index=True, nullable=False)
    day_index: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str | None] = mapped_column(String(128), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_cost_low: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost_high: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_transport_time_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_walking_distance_meters: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    weather_summary: Mapped[str | None] = mapped_column(String(256), nullable=True)

    plan = relationship("ItineraryPlan", back_populates="daily_routes")
    route_items = relationship("RouteItem", back_populates="daily_route")


class RouteItem(Base, TimestampMixin):
    __tablename__ = "route_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    daily_route_id: Mapped[int] = mapped_column(ForeignKey("daily_routes.id"), index=True, nullable=False)
    poi_id: Mapped[int] = mapped_column(ForeignKey("pois.id"), index=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[str | None] = mapped_column(String(16), nullable=True)
    end_time: Mapped[str | None] = mapped_column(String(16), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    transport_to_next: Mapped[str | None] = mapped_column(String(32), nullable=True)
    distance_to_next_meters: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_to_next_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    route_polyline_to_next: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    tips: Mapped[str | None] = mapped_column(Text, nullable=True)

    daily_route = relationship("DailyRoute", back_populates="route_items")
    poi = relationship("Poi", back_populates="route_items")
