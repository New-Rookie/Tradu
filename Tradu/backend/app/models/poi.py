from sqlalchemy import Boolean, Float, Integer, JSON, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.base_mixins import TimestampMixin


class Poi(Base, TimestampMixin):
    __tablename__ = "pois"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    poi_name: Mapped[str] = mapped_column(String(128), nullable=False)
    poi_alias: Mapped[str | None] = mapped_column(String(256), nullable=True)
    city: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    district: Mapped[str | None] = mapped_column(String(64), nullable=True)
    poi_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    recommended_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    best_time: Mapped[str | None] = mapped_column(String(128), nullable=True)
    avoid_time: Mapped[str | None] = mapped_column(String(128), nullable=True)
    price_level: Mapped[str] = mapped_column(String(32), nullable=False)
    estimated_cost_low: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost_high: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    indoor_outdoor: Mapped[str] = mapped_column(String(32), nullable=False)
    suitable_for: Mapped[list | None] = mapped_column(JSON, nullable=True)
    avoid_tips: Mapped[str | None] = mapped_column(Text, nullable=True)
    nearby_area: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)

    amap_poi_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    amap_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    amap_address: Mapped[str | None] = mapped_column(String(256), nullable=True)
    amap_type: Mapped[str | None] = mapped_column(String(256), nullable=True)
    amap_cityname: Mapped[str | None] = mapped_column(String(64), nullable=True)
    amap_adname: Mapped[str | None] = mapped_column(String(64), nullable=True)
    match_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    match_status: Mapped[str] = mapped_column(String(32), default="not_found", nullable=False)
    match_keyword: Mapped[str | None] = mapped_column(String(128), nullable=True)

    source: Mapped[str] = mapped_column(String(32), default="manual", nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.8, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    content_knowledge = relationship("ContentKnowledge", back_populates="poi")
    route_items = relationship("RouteItem", back_populates="poi")

    __table_args__ = (
        Index("idx_pois_city_type", "city", "poi_type"),
        Index("idx_pois_city_area", "city", "nearby_area"),
    )
