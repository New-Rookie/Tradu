from sqlalchemy import Float, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.models.base_mixins import TimestampMixin


class ServicePoi(Base, TimestampMixin):
    __tablename__ = "service_pois"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    amap_poi_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    city: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    district: Mapped[str | None] = mapped_column(String(64), nullable=True)
    nearby_area: Mapped[str | None] = mapped_column(String(128), nullable=True)
    address: Mapped[str | None] = mapped_column(String(256), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    service_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    poi_type: Mapped[str | None] = mapped_column(String(256), nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_level: Mapped[str] = mapped_column(String(32), default="unknown", nullable=False)
    business_area: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="amap", nullable=False)
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    last_updated_at: Mapped[str | None] = mapped_column(String(32), nullable=True)

    __table_args__ = (
        Index("idx_service_pois_city_type_area", "city", "service_type", "nearby_area"),
    )


class HotelArea(Base, TimestampMixin):
    __tablename__ = "hotel_areas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    city: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    area_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    district: Mapped[str | None] = mapped_column(String(64), nullable=True)
    center_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    center_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    budget_level: Mapped[str] = mapped_column(String(32), default="medium", nullable=False)
    transport_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    food_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    attraction_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    night_activity_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    suitable_for: Mapped[list | None] = mapped_column(JSON, nullable=True)
    risk_tips: Mapped[list | None] = mapped_column(JSON, nullable=True)
    recommendation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="system", nullable=False)
    last_updated_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
