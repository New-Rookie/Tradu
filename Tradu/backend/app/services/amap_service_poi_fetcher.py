from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List

import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.models.service_poi import ServicePoi

AMAP_TYPES = {
    "restaurant": "050000",
    "hotel": "100000",
    "shopping": "060000",
    "rest": "080000|110000",
}


class AMapServicePoiFetcher:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.base_url = self.settings.amap_web_service_base_url.rstrip("/")
        self.key = self.settings.amap_web_service_key

    def fetch_restaurants_nearby(self, city: str, longitude: float, latitude: float, radius: int = 2000) -> List[Dict[str, Any]]:
        return self._fetch_nearby(city, longitude, latitude, "restaurant", radius)

    def fetch_hotels_nearby(self, city: str, longitude: float, latitude: float, radius: int = 3000) -> List[Dict[str, Any]]:
        return self._fetch_nearby(city, longitude, latitude, "hotel", radius)

    def fetch_shopping_nearby(self, city: str, longitude: float, latitude: float, radius: int = 2000) -> List[Dict[str, Any]]:
        return self._fetch_nearby(city, longitude, latitude, "shopping", radius)

    def fetch_service_pois_by_area(self, city: str, nearby_area: str, service_type: str) -> List[ServicePoi]:
        stmt = select(ServicePoi).where(ServicePoi.city == city, ServicePoi.service_type == service_type, ServicePoi.nearby_area == nearby_area).order_by(ServicePoi.rating.desc().nullslast(), ServicePoi.id.asc())
        return list(self.db.execute(stmt).scalars().all())

    def upsert_service_pois(self, pois: Iterable[Dict[str, Any]]) -> Dict[str, int]:
        inserted = 0
        updated = 0
        for data in pois:
            amap_id = data.get("amap_poi_id")
            existing = None
            if amap_id:
                existing = self.db.execute(select(ServicePoi).where(ServicePoi.amap_poi_id == amap_id)).scalar_one_or_none()
            if existing is None:
                existing = ServicePoi(**data)
                self.db.add(existing)
                inserted += 1
            else:
                for key, value in data.items():
                    if key != "id":
                        setattr(existing, key, value)
                updated += 1
        self.db.commit()
        return {"inserted": inserted, "updated": updated}

    def is_cache_expired(self, city: str, service_type: str, nearby_area: str, max_age_days: int = 3) -> bool:
        newest = self.db.execute(select(ServicePoi).where(ServicePoi.city == city, ServicePoi.service_type == service_type, ServicePoi.nearby_area == nearby_area).order_by(ServicePoi.updated_at.desc())).scalar_one_or_none()
        if newest is None:
            return True
        return newest.updated_at < datetime.utcnow() - timedelta(days=max_age_days)

    def refresh_area_service_pois(self, city: str, nearby_area: str, center: Dict[str, float] | None = None, service_types: List[str] | None = None) -> Dict[str, int]:
        center = center or self._area_center(city, nearby_area)
        service_types = service_types or ["restaurant", "hotel", "shopping"]
        totals = {"inserted": 0, "updated": 0}
        for service_type in service_types:
            raw = self._fetch_nearby(city, center["longitude"], center["latitude"], service_type, 3000 if service_type == "hotel" else 2000)
            for poi in raw:
                poi["nearby_area"] = nearby_area
            result = self.upsert_service_pois(raw)
            totals["inserted"] += result["inserted"]
            totals["updated"] += result["updated"]
        return totals

    def _fetch_nearby(self, city: str, longitude: float, latitude: float, service_type: str, radius: int) -> List[Dict[str, Any]]:
        if not self.key:
            return []
        params = {"key": self.key, "location": f"{longitude},{latitude}", "radius": radius, "types": AMAP_TYPES.get(service_type, ""), "city": city, "offset": 20, "page": 1, "extensions": "all", "output": "JSON"}
        resp = requests.get(f"{self.base_url}/v3/place/around", params=params, timeout=10)
        resp.raise_for_status()
        payload = resp.json()
        return [self._normalize_amap_poi(x, city, service_type) for x in payload.get("pois", [])]

    def _normalize_amap_poi(self, item: Dict[str, Any], city: str, service_type: str) -> Dict[str, Any]:
        location = str(item.get("location") or ",").split(",")
        biz = item.get("biz_ext") if isinstance(item.get("biz_ext"), dict) else {}
        cost = self._as_float(biz.get("cost") or item.get("cost"))
        rating = self._as_float(biz.get("rating") or item.get("rating"))
        return {
            "amap_poi_id": item.get("id") or None,
            "name": item.get("name") or "未命名服务点",
            "city": city or item.get("cityname") or "",
            "district": item.get("adname") or None,
            "nearby_area": None,
            "address": item.get("address") if isinstance(item.get("address"), str) else None,
            "longitude": self._as_float(location[0]) if len(location) > 0 else None,
            "latitude": self._as_float(location[1]) if len(location) > 1 else None,
            "service_type": service_type,
            "poi_type": item.get("type") or None,
            "tags": [x for x in str(item.get("type") or "").split(";") if x],
            "rating": rating,
            "cost": cost,
            "price_level": self._price_level(cost, service_type),
            "business_area": item.get("business_area") or item.get("biz_type") or None,
            "source": "amap",
            "raw_payload": {k: item.get(k) for k in ["id", "name", "type", "address", "location", "biz_ext", "business_area"]},
            "last_updated_at": datetime.utcnow().isoformat(),
        }

    def _area_center(self, city: str, nearby_area: str) -> Dict[str, float]:
        # 重庆核心区默认兜底，调用方可以传入更精确中心点。
        defaults = {
            "解放碑片区": {"longitude": 106.576, "latitude": 29.557},
            "观音桥片区": {"longitude": 106.532, "latitude": 29.580},
            "沙坪坝片区": {"longitude": 106.457, "latitude": 29.541},
        }
        return defaults.get(nearby_area, {"longitude": 106.5516, "latitude": 29.5630})

    @staticmethod
    def _as_float(value: Any) -> float | None:
        try:
            if value in {None, "", []}:
                return None
            return float(value)
        except Exception:
            return None

    @staticmethod
    def _price_level(cost: float | None, service_type: str) -> str:
        if cost is None:
            return "unknown"
        if cost <= 0:
            return "free"
        if service_type == "hotel":
            return "low" if cost < 250 else "medium" if cost < 600 else "high"
        return "low" if cost < 60 else "medium" if cost < 150 else "high"
