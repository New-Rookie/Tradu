from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.base_mixins import TimestampMixin


class GuideImport(Base, TimestampMixin):
    __tablename__ = "guide_imports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    destination: Mapped[str | None] = mapped_column(String(64), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    raw_text_hash: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    extract_status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="guide_imports")
    extracted_pois = relationship("GuideExtractedPoi", back_populates="guide_import")


class GuideExtractedPoi(Base, TimestampMixin):
    __tablename__ = "guide_extracted_pois"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    guide_import_id: Mapped[int] = mapped_column(ForeignKey("guide_imports.id"), index=True, nullable=False)
    raw_name: Mapped[str] = mapped_column(String(128), nullable=False)
    normalized_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    poi_id: Mapped[int | None] = mapped_column(ForeignKey("pois.id"), index=True, nullable=True)
    amap_poi_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    poi_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    recommended_time: Mapped[str | None] = mapped_column(String(128), nullable=True)
    suggested_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tips: Mapped[list | None] = mapped_column(JSON, nullable=True)
    match_status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    user_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    guide_import = relationship("GuideImport", back_populates="extracted_pois")
    poi = relationship("Poi")
