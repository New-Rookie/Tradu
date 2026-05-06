from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.service_poi import HotelArea, ServicePoi


class HotelAreaService:
    def __init__(self, db: Session | None = None):
        self.db = db

    def recommend_hotel_area(self, city: str, user_request: Dict[str, Any], candidate_areas: Iterable[str]) -> Dict[str, Any]:
        areas = list(candidate_areas) or ["解放碑片区"]
        db_areas = self._load_db_areas(city)
        route_areas = Counter(areas)
        if db_areas:
            scored = [(area, self.score_hotel_area(area, user_request, route_areas)) for area in db_areas]
            best = max(scored, key=lambda x: x[1])[0]
            area_name = best.area_name
            reason = best.recommendation_reason or self._default_reason(area_name)
            risk_tips = best.risk_tips or ["节假日酒店价格波动较大", "热门片区晚间人流较多"]
            budget_level = best.budget_level
            lon, lat = best.center_longitude, best.center_latitude
        else:
            area_name = route_areas.most_common(1)[0][0]
            budget_level = self._budget_level(user_request)
            reason = self._default_reason(area_name)
            risk_tips = ["V1 仅推荐住宿区域与参考酒店，不提供实时预订价格", "热门景区周边节假日可能拥挤"]
            lon, lat = self._fallback_center(area_name)
        return {
            "item_type": "hotel_area",
            "area_name": area_name,
            "poi_name": area_name,
            "budget_level": budget_level,
            "longitude": lon,
            "latitude": lat,
            "reason": reason,
            "risk_tips": risk_tips,
            "reference_hotels": self.get_hotels_for_reference(city, area_name),
        }

    def score_hotel_area(self, area: HotelArea, user_request: Dict[str, Any], route_areas: Counter) -> float:
        score = route_areas.get(area.area_name, 0) * 20
        score += area.transport_score * 0.25 + area.food_score * 0.2 + area.attraction_score * 0.25 + area.night_activity_score * 0.15
        prefs = user_request.get("preferences") or []
        if any("美食" in p for p in prefs):
            score += area.food_score * 0.15
        if any("夜景" in p for p in prefs):
            score += area.night_activity_score * 0.15
        if self._budget_level(user_request) == area.budget_level:
            score += 8
        return round(score, 2)

    def get_hotels_for_reference(self, city: str, area_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        if self.db is None:
            return []
        rows = self.db.execute(select(ServicePoi).where(ServicePoi.city == city, ServicePoi.service_type == "hotel", ServicePoi.nearby_area == area_name).limit(limit)).scalars().all()
        return [{"name": r.name, "address": r.address, "rating": r.rating, "cost": r.cost, "price_level": r.price_level, "longitude": r.longitude, "latitude": r.latitude} for r in rows]

    def _load_db_areas(self, city: str) -> List[HotelArea]:
        if self.db is None:
            return []
        return list(self.db.execute(select(HotelArea).where(HotelArea.city == city)).scalars().all())

    @staticmethod
    def _budget_level(user_request: Dict[str, Any]) -> str:
        budget = float(user_request.get("budget") or user_request.get("budget_limit") or 0)
        days = max(int(user_request.get("days") or 1), 1)
        per_day = budget / days if budget else 0
        if per_day and per_day < 500:
            return "low"
        if per_day > 1200:
            return "high"
        return "medium"

    @staticmethod
    def _fallback_center(area_name: str) -> tuple[float, float]:
        centers = {"解放碑片区": (106.576, 29.557), "观音桥片区": (106.532, 29.580), "沙坪坝片区": (106.457, 29.541)}
        return centers.get(area_name, (106.5516, 29.5630))

    @staticmethod
    def _default_reason(area_name: str) -> str:
        return f"{area_name}与当前路线覆盖片区匹配度高，方便夜间返回和次日出发。住宿仅做区域建议，不承诺实时房价。"
