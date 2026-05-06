from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy.orm import Session

from backend.app.services.formal_itinerary_service import FormalItineraryService
from backend.app.services.itinerary_state_service import ItineraryStateService


class ItineraryAdjustmentService:
    def __init__(self, db: Session):
        self.db = db
        self.state_service = ItineraryStateService(db)

    def adjust_by_instruction(self, session_id: str, instruction: str) -> Dict[str, Any]:
        parsed = self._parse_instruction(instruction)
        state = self._apply_actions(session_id, parsed["actions"], parsed.get("memory_updates", {}))
        itinerary = self._regenerate_from_state(state)
        explanation = self._explanation(parsed["actions"], state)
        self.state_service.save_latest_itinerary(session_id, itinerary)
        return {"adjustment_actions": parsed["actions"], "itinerary": itinerary, "explanation": explanation}

    def regenerate_after_state_action(self, session_id: str, action: str, **kwargs: Any) -> Dict[str, Any]:
        if action == "remove_poi":
            state = self.state_service.apply_remove_poi(session_id, kwargs["poi_name"])
        elif action == "reduce_walking":
            state = self.state_service.apply_reduce_walking(session_id)
        elif action == "rain_mode":
            state = self.state_service.apply_rain_mode(session_id)
        elif action == "compress_day":
            state = self.state_service.apply_compress_day(session_id, int(kwargs["day_index"]))
        elif action == "continue_from_current_location":
            state = self.state_service.apply_current_location(session_id, float(kwargs["longitude"]), float(kwargs["latitude"]), kwargs.get("current_time"))
        else:
            state = self.state_service.get_state(session_id)
        itinerary = self._regenerate_from_state(state)
        self.state_service.save_latest_itinerary(session_id, itinerary)
        return {"adjustment_actions": [{"action_type": action, **kwargs}], "itinerary": itinerary, "explanation": self._explanation([{"action_type": action}], state)}

    def _parse_instruction(self, instruction: str) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = []
        memory = {"removed_pois": [], "preferences": [], "avoid": []}
        if "洪崖洞" in instruction and any(x in instruction for x in ["不想去", "删除", "别去", "不去"]):
            actions.append({"action_type": "remove_poi", "target_poi": "洪崖洞", "priority": "hard_constraint", "reason": "用户明确表示不想去"})
            memory["removed_pois"].append("洪崖洞")
        if "少走" in instruction or "不想太累" in instruction:
            actions.append({"action_type": "reduce_walking", "priority": "soft_constraint", "reason": "用户希望降低步行强度"})
            memory["walking_tolerance"] = "low"
        if "美食" in instruction or "餐饮" in instruction or "吃" in instruction:
            actions.append({"action_type": "increase_preference", "target_preference": "美食", "priority": "soft_constraint", "reason": "用户希望增加美食体验"})
            memory["preferences"].append("美食")
        if "雨" in instruction:
            actions.append({"action_type": "rain_mode", "priority": "soft_constraint", "reason": "用户提到雨天"})
        if not actions:
            actions.append({"action_type": "note", "priority": "soft_constraint", "reason": "记录用户自然语言调整"})
        return {"actions": actions, "memory_updates": memory, "need_regenerate": True, "affected_scope": "current_plan", "user_message": "已理解你的调整要求。"}

    def _apply_actions(self, session_id: str, actions: List[Dict[str, Any]], memory: Dict[str, Any]):
        state = self.state_service.get_state(session_id) or self.state_service._require_state(session_id)
        for poi_name in memory.get("removed_pois", []):
            state = self.state_service.apply_remove_poi(session_id, poi_name)
        if memory.get("walking_tolerance") == "low":
            state = self.state_service.apply_reduce_walking(session_id)
        if memory.get("preferences") or memory.get("avoid"):
            state = self.state_service.apply_preference_change(session_id, memory.get("preferences"), memory.get("avoid"))
        if any(a.get("action_type") == "rain_mode" for a in actions):
            state = self.state_service.apply_rain_mode(session_id)
        return state

    def _regenerate_from_state(self, state) -> Dict[str, Any]:
        old = state.latest_itinerary_payload or {}
        req = {
            "session_id": state.session_id,
            "destination": state.destination or old.get("destination") or "重庆",
            "days": state.days or len((old.get("plans") or [{}])[0].get("days", [])) or 1,
            "budget": state.budget_limit or (state.budget_plan or {}).get("total_budget"),
            "preferences": state.preferences or [],
            "avoid": state.avoid or [],
            "travel_style": state.travel_style or "standard",
            "walking_tolerance": state.walking_tolerance or "medium",
            "transport_preference": state.transport_preference or "public_transport",
            "removed_pois": state.removed_pois or [],
            "confirmed_pois": state.confirmed_pois or [],
            "weather_mode": state.weather_mode,
            "current_location": state.current_location,
            "compress_day_index": state.selected_day_index if (state.adjustment_history and state.adjustment_history[-1].get("action") == "compress_day") else None,
            "need_meal_planning": True,
            "need_hotel_area": True,
        }
        return FormalItineraryService(self.db).generate_itinerary(req)

    @staticmethod
    def _explanation(actions: List[Dict[str, Any]], state) -> str:
        names = [a.get("target_poi") for a in actions if a.get("action_type") == "remove_poi" and a.get("target_poi")]
        parts = []
        if names:
            parts.append(f"已删除{ '、'.join(names) }，后续路线不会再安排这些点位。")
        if any(a.get("action_type") == "reduce_walking" for a in actions) or getattr(state, "walking_tolerance", "") == "low":
            parts.append("已降低步行强度，优先同片区与公共交通/打车衔接。")
        if any(a.get("action_type") == "rain_mode" for a in actions) or getattr(state, "weather_mode", "") == "rainy":
            parts.append("已切换雨天方案，提高室内、商圈和餐饮点位权重。")
        if any(a.get("action_type") == "increase_preference" for a in actions):
            parts.append("已增加美食相关安排。")
        return "".join(parts) or "已基于当前 itinerary_state 保存调整并重新生成路线。"
