from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.service_poi import ServicePoi


class MealPlanner:
    def __init__(self, db: Session | None = None):
        self.db = db

    def insert_meal_slots(self, day_route: Dict[str, Any], user_request: Dict[str, Any], budget_plan: Dict[str, Any]) -> Dict[str, Any]:
        items = list(day_route.get("items") or [])
        if not items:
            return day_route
        budget_level = self._budget_level(budget_plan)
        city = user_request.get("destination") or user_request.get("city") or "重庆"
        lunch_anchor = items[max(0, min(len(items) - 1, len(items) // 2 - 1))]
        dinner_anchor = items[-1]
        lunch = self.select_restaurant_candidate(self.find_lunch_candidates(city, lunch_anchor.get("longitude"), lunch_anchor.get("latitude"), budget_level), user_request)
        dinner = self.select_restaurant_candidate(self.find_dinner_candidates(city, dinner_anchor.get("longitude"), dinner_anchor.get("latitude"), budget_level), user_request)
        lunch_item = self._meal_item("lunch", lunch, lunch_anchor, budget_level, len(items) + 1)
        dinner_item = self._meal_item("dinner", dinner, dinner_anchor, budget_level, len(items) + 2)
        split = max(1, len(items) // 2)
        new_items = items[:split] + [lunch_item] + items[split:] + [dinner_item]
        for i, item in enumerate(new_items, 1):
            item["sort_order"] = i
        day_route["items"] = new_items
        day_route["estimated_cost_low"] = int(day_route.get("estimated_cost_low") or 0) + lunch_item["estimated_cost_low"] + dinner_item["estimated_cost_low"]
        day_route["estimated_cost_high"] = int(day_route.get("estimated_cost_high") or 0) + lunch_item["estimated_cost_high"] + dinner_item["estimated_cost_high"]
        day_route["budget_detail"] = self._budget_detail(day_route, budget_plan)
        return day_route

    def find_lunch_candidates(self, city: str, longitude: float | None, latitude: float | None, budget_level: str) -> List[Dict[str, Any]]:
        return self._find_candidates(city, budget_level)

    def find_dinner_candidates(self, city: str, longitude: float | None, latitude: float | None, budget_level: str) -> List[Dict[str, Any]]:
        return self._find_candidates(city, budget_level)

    def select_restaurant_candidate(self, candidates: List[Dict[str, Any]], user_request: Dict[str, Any]) -> Dict[str, Any] | None:
        if not candidates:
            return None
        prefs = " ".join(user_request.get("preferences") or [])
        if "美食" in prefs or "火锅" in prefs:
            return sorted(candidates, key=lambda x: (x.get("rating") or 0, -(x.get("cost") or 999)), reverse=True)[0]
        return candidates[0]

    def estimate_meal_cost(self, restaurant: Dict[str, Any] | None, budget_level: str) -> tuple[int, int]:
        if restaurant and restaurant.get("cost"):
            cost = int(float(restaurant["cost"]))
            return max(15, int(cost * 0.8)), max(30, int(cost * 1.25))
        return {"low": (25, 60), "medium": (50, 120), "high": (100, 220)}.get(budget_level, (40, 100))

    def _find_candidates(self, city: str, budget_level: str) -> List[Dict[str, Any]]:
        if self.db is None:
            return []
        stmt = select(ServicePoi).where(ServicePoi.city == city, ServicePoi.service_type == "restaurant")
        if budget_level in {"low", "medium", "high"}:
            stmt = stmt.where(ServicePoi.price_level.in_([budget_level, "unknown", "low"] if budget_level == "low" else [budget_level, "unknown", "low", "medium"]))
        rows = self.db.execute(stmt.limit(10)).scalars().all()
        return [{"poi_name": r.name, "name": r.name, "nearby_area": r.nearby_area, "longitude": r.longitude, "latitude": r.latitude, "rating": r.rating, "cost": r.cost, "price_level": r.price_level, "address": r.address} for r in rows]

    def _meal_item(self, meal_type: str, restaurant: Dict[str, Any] | None, anchor: Dict[str, Any], budget_level: str, sort_order: int) -> Dict[str, Any]:
        low, high = self.estimate_meal_cost(restaurant, budget_level)
        name = (restaurant or {}).get("poi_name") or (anchor.get("nearby_area") or "附近餐饮区")
        return {
            "sort_order": sort_order,
            "item_type": "meal",
            "meal_type": meal_type,
            "poi_id": None,
            "poi_name": name,
            "poi_type": "餐饮",
            "service_type": "restaurant",
            "nearby_area": (restaurant or {}).get("nearby_area") or anchor.get("nearby_area"),
            "longitude": (restaurant or {}).get("longitude") or anchor.get("longitude"),
            "latitude": (restaurant or {}).get("latitude") or anchor.get("latitude"),
            "suggested_duration_minutes": 60,
            "estimated_cost_low": low,
            "estimated_cost_high": high,
            "reason": f"位于当天路线{'中段' if meal_type == 'lunch' else '收尾'}，按{budget_level}预算做餐饮补给估算。",
            "tips": "餐饮价格为预算约束估算，不代表实时菜单价格。",
        }

    @staticmethod
    def _budget_level(budget_plan: Dict[str, Any]) -> str:
        warning = budget_plan.get("budget_warning")
        return "low" if warning == "budget_tight" else "high" if warning == "budget_flexible" else "medium"

    @staticmethod
    def _budget_detail(day_route: Dict[str, Any], budget_plan: Dict[str, Any]) -> Dict[str, Any]:
        return {"attraction_estimate": day_route.get("estimated_cost_low", 0), "food_daily_cap": budget_plan.get("daily_food_budget", 0), "transport_daily_cap": budget_plan.get("daily_transport_budget", 0), "note": "预算约束估算，非实时价格。"}
