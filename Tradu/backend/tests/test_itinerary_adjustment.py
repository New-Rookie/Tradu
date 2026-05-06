from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app import models  # noqa: F401
from backend.app.db.base import Base
from backend.app.services.formal_itinerary_service import FormalItineraryService
from backend.app.services.itinerary_adjustment_service import ItineraryAdjustmentService
from backend.app.services.itinerary_state_service import ItineraryStateService


def make_db():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()


def flatten_names(itinerary):
    return [i.get("poi_name") for p in itinerary["plans"] for d in p["days"] for i in d["items"]]


def test_adjustment_removes_hongyadong_and_adds_food():
    db = make_db()
    payload = FormalItineraryService(db).generate_itinerary({"destination": "重庆", "days": 2, "budget": 2500, "preferences": ["美食"], "need_meal_planning": True})
    ItineraryStateService(db).create_or_update_state("s1", payload, {"destination": "重庆", "days": 2, "budget": 2500, "preferences": ["美食"]})
    result = ItineraryAdjustmentService(db).adjust_by_instruction("s1", "我不想去洪崖洞，少走路一点，多安排美食。")
    state = ItineraryStateService(db).get_state("s1")
    assert "洪崖洞" in state.removed_pois
    assert "洪崖洞" not in flatten_names(result["itinerary"])
    assert result["explanation"]
