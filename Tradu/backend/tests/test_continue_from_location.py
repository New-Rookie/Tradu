from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app import models  # noqa: F401
from backend.app.db.base import Base
from backend.app.services.formal_itinerary_service import FormalItineraryService
from backend.app.services.itinerary_adjustment_service import ItineraryAdjustmentService
from backend.app.services.itinerary_state_service import ItineraryStateService


def test_continue_from_location_regenerates_route():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine, future=True)()
    payload = FormalItineraryService(db).generate_itinerary({"destination": "重庆", "days": 1, "budget": 1000})
    ItineraryStateService(db).create_or_update_state("loc", payload, {"destination": "重庆", "days": 1, "budget": 1000})
    result = ItineraryAdjustmentService(db).regenerate_after_state_action("loc", "continue_from_current_location", longitude=106.575, latitude=29.557, current_time="15:30")
    assert result["itinerary"]["plans"][0]["days"][0]["items"]
