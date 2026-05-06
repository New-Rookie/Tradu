from sqlalchemy import Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.base_mixins import TimestampMixin


class ContentKnowledge(Base, TimestampMixin):
    __tablename__ = "content_knowledge"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    poi_id: Mapped[int | None] = mapped_column(ForeignKey("pois.id"), index=True, nullable=True)
    city: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    raw_text_hash: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    positive_tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    negative_tips: Mapped[list | None] = mapped_column(JSON, nullable=True)
    recommended_time: Mapped[str | None] = mapped_column(String(128), nullable=True)
    suggested_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    heat_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.8, nullable=False)

    poi = relationship("Poi", back_populates="content_knowledge")
