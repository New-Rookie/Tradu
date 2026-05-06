from sqlalchemy import Float, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.base_mixins import TimestampMixin


class ItineraryState(Base, TimestampMixin):
    __tablename__ = "itinerary_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    itinerary_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    destination: Mapped[str | None] = mapped_column(String(64), nullable=True)
    days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    budget_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    budget_plan: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    preferences: Mapped[list | None] = mapped_column(JSON, nullable=True)
    avoid: Mapped[list | None] = mapped_column(JSON, nullable=True)
    travel_style: Mapped[str | None] = mapped_column(String(32), nullable=True)
    walking_tolerance: Mapped[str] = mapped_column(String(32), default="medium", nullable=False)
    transport_preference: Mapped[str | None] = mapped_column(String(32), nullable=True)
    selected_plan_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    selected_day_index: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    hotel_area: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    locked_pois: Mapped[list | None] = mapped_column(JSON, nullable=True)
    removed_pois: Mapped[list | None] = mapped_column(JSON, nullable=True)
    confirmed_pois: Mapped[list | None] = mapped_column(JSON, nullable=True)
    replaced_pois: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    weather_mode: Mapped[str] = mapped_column(String(32), default="normal", nullable=False)
    current_location: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    latest_itinerary_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    adjustment_history: Mapped[list | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (Index("idx_itinerary_states_session_itinerary", "session_id", "itinerary_id"),)


class UserSession(Base, TimestampMixin):
    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_destination: Mapped[str | None] = mapped_column(String(64), nullable=True)
    current_itinerary_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    last_active_at: Mapped[str | None] = mapped_column(String(32), nullable=True)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(32), default="general", nullable=False)
    structured_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
