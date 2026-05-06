from sqlalchemy import ForeignKey, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.base_mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(64), nullable=True)
    email: Mapped[str | None] = mapped_column(String(128), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)

    profiles = relationship("UserProfile", back_populates="user")
    itineraries = relationship("Itinerary", back_populates="user")
    guide_imports = relationship("GuideImport", back_populates="user")


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    destination: Mapped[str] = mapped_column(String(64), nullable=False)
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    budget: Mapped[int | None] = mapped_column(Integer, nullable=True)
    travel_style: Mapped[str] = mapped_column(String(32), default="standard", nullable=False)
    walking_tolerance: Mapped[str] = mapped_column(String(32), default="medium", nullable=False)
    transport_preference: Mapped[str] = mapped_column(String(32), default="mixed", nullable=False)
    preferences: Mapped[list | None] = mapped_column(JSON, nullable=True)
    avoid_preferences: Mapped[list | None] = mapped_column(JSON, nullable=True)

    user = relationship("User", back_populates="profiles")
