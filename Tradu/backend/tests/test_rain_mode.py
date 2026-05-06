from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app import models  # noqa: F401
from backend.app.db.base import Base
from backend.app.services.formal_itinerary_service import FormalItineraryService
from backend.app.services.itinerary_adjustment_service import ItineraryAdjustmentService
from backend.app.services.itinerary_state_service import ItineraryStateService


def test_rain_mode_returns_explanation():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine, future=True)()
    payload = FormalItineraryService(db).generate_itinerary({"destination": "重庆", "days": 1, "budget": 1000})
    ItineraryStateService(db).create_or_update_state("rain", payload, {"destination": "重庆", "days": 1, "budget": 1000})
    result = ItineraryAdjustmentService(db).regenerate_after_state_action("rain", "rain_mode")
    assert "雨天" in result["explanation"]
    assert result["itinerary"]["plans"]
