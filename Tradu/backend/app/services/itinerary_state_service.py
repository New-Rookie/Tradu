from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.session_state import ItineraryState


class ItineraryStateService:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update_state(self, session_id: str, itinerary_payload: Dict[str, Any], user_request: Dict[str, Any]) -> ItineraryState:
        state = self.get_state(session_id)
        if state is None:
            state = ItineraryState(session_id=session_id)
            self.db.add(state)
        state.itinerary_id = itinerary_payload.get("itinerary_id")
        state.destination = user_request.get("destination")
        state.days = user_request.get("days")
        state.budget_limit = user_request.get("budget")
        state.budget_plan = itinerary_payload.get("budget_plan")
        state.preferences = user_request.get("preferences") or []
        state.avoid = user_request.get("avoid") or []
        state.travel_style = user_request.get("travel_style")
        state.walking_tolerance = user_request.get("walking_tolerance") or state.walking_tolerance or "medium"
        state.transport_preference = user_request.get("transport_preference")
        state.hotel_area = itinerary_payload.get("recommended_hotel_area")
        state.latest_itinerary_payload = itinerary_payload
        state.adjustment_history = state.adjustment_history or []
        self.db.commit()
        self.db.refresh(state)
        return state

    def get_state(self, session_id: str) -> ItineraryState | None:
        return self.db.execute(select(ItineraryState).where(ItineraryState.session_id == session_id)).scalar_one_or_none()

    def apply_remove_poi(self, session_id: str, poi_name: str) -> ItineraryState:
        state = self._require_state(session_id)
        state.removed_pois = sorted(set((state.removed_pois or []) + [poi_name]))
        self._append_history(state, "remove_poi", {"poi_name": poi_name})
        self.db.commit()
        return state

    def apply_reduce_walking(self, session_id: str) -> ItineraryState:
        state = self._require_state(session_id)
        state.walking_tolerance = "low"
        state.transport_preference = "public_transport"
        self._append_history(state, "reduce_walking", {})
        self.db.commit()
        return state

    def apply_rain_mode(self, session_id: str) -> ItineraryState:
        state = self._require_state(session_id)
        state.weather_mode = "rainy"
        avoid = set(state.avoid or [])
        avoid.update(["户外长时间步行", "citywalk"])
        state.avoid = sorted(avoid)
        self._append_history(state, "rain_mode", {})
        self.db.commit()
        return state

    def apply_compress_day(self, session_id: str, day_index: int) -> ItineraryState:
        state = self._require_state(session_id)
        state.selected_day_index = day_index
        self._append_history(state, "compress_day", {"day_index": day_index})
        self.db.commit()
        return state

    def apply_current_location(self, session_id: str, longitude: float, latitude: float, current_time: str | None = None) -> ItineraryState:
        state = self._require_state(session_id)
        state.current_location = {"longitude": longitude, "latitude": latitude, "current_time": current_time}
        self._append_history(state, "continue_from_current_location", state.current_location)
        self.db.commit()
        return state

    def apply_preference_change(self, session_id: str, preferences: List[str] | None = None, avoid: List[str] | None = None) -> ItineraryState:
        state = self._require_state(session_id)
        if preferences:
            state.preferences = sorted(set((state.preferences or []) + preferences))
        if avoid:
            state.avoid = sorted(set((state.avoid or []) + avoid))
        self._append_history(state, "preference_change", {"preferences": preferences or [], "avoid": avoid or []})
        self.db.commit()
        return state

    def save_latest_itinerary(self, session_id: str, itinerary_payload: Dict[str, Any]) -> ItineraryState:
        state = self._require_state(session_id)
        state.latest_itinerary_payload = itinerary_payload
        state.itinerary_id = itinerary_payload.get("itinerary_id")
        state.budget_plan = itinerary_payload.get("budget_plan") or state.budget_plan
        self.db.commit()
        return state

    def to_dict(self, state: ItineraryState | None) -> Dict[str, Any] | None:
        if state is None:
            return None
        return {c.name: getattr(state, c.name) for c in state.__table__.columns if c.name not in {"id"}}

    def _require_state(self, session_id: str) -> ItineraryState:
        state = self.get_state(session_id)
        if state is None:
            state = ItineraryState(session_id=session_id, adjustment_history=[], removed_pois=[], confirmed_pois=[], locked_pois=[])
            self.db.add(state)
            self.db.commit()
            self.db.refresh(state)
        return state

    @staticmethod
    def _append_history(state: ItineraryState, action: str, payload: Dict[str, Any]) -> None:
        history = list(state.adjustment_history or [])
        history.append({"action": action, "payload": payload, "created_at": datetime.utcnow().isoformat()})
        state.adjustment_history = history
