from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from sqlalchemy import text
except Exception:  # pragma: no cover
    text = None

from backend.app.planners.itinerary_optimizer import ItineraryOptimizer


class FormalItineraryService:
    """
    正式行程生成服务。

    设计原则：
    1. 优先从数据库 pois 表读取 POI；
    2. 如果数据库不可用，则从 data/processed/chongqing_pois_enriched.csv 兜底读取；
    3. 对外提供 generate_itinerary 方法，兼容 dict 和 Pydantic 请求对象；
    4. 输出结构与第六步 API 骨架中的临时方案结构保持兼容。
    """

    def __init__(self, db: Any = None):
        self.db = db

    def generate_itinerary(self, request: Any, weather: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        user_request = self._request_to_dict(request)
        user_request = self._normalize_request(user_request)

        pois = self._load_pois(city=user_request.get("destination", "重庆"))
        if not pois:
            raise RuntimeError("No POI data available. Please seed pois table or provide data/processed/chongqing_pois_enriched.csv")

        optimizer = ItineraryOptimizer(pois)
        return optimizer.generate(user_request=user_request, weather=weather)

    @staticmethod
    def _request_to_dict(request: Any) -> Dict[str, Any]:
        if isinstance(request, dict):
            return dict(request)
        if hasattr(request, "model_dump"):
            return request.model_dump()
        if hasattr(request, "dict"):
            return request.dict()
        raise TypeError(f"Unsupported request type: {type(request)}")

    @staticmethod
    def _normalize_request(data: Dict[str, Any]) -> Dict[str, Any]:
        destination = data.get("destination") or data.get("city") or "重庆"
        days = int(data.get("days") or 1)
        days = max(1, min(days, 7))

        budget = data.get("budget")
        try:
            budget = float(budget) if budget not in {None, ""} else 0.0
        except Exception:
            budget = 0.0

        return {
            "destination": destination,
            "days": days,
            "budget": budget,
            "preferences": data.get("preferences") or [],
            "avoid": data.get("avoid") or [],
            "travel_style": data.get("travel_style") or "standard",
            "walking_tolerance": data.get("walking_tolerance") or "medium",
            "transport_preference": data.get("transport_preference") or "public_transport",
            "need_weather_adjustment": data.get("need_weather_adjustment", False),
            "has_imported_note": data.get("has_imported_note", False),
        }

    def _load_pois(self, city: str = "重庆") -> List[Dict[str, Any]]:
        db_rows = self._load_pois_from_db(city=city)
        if db_rows:
            return db_rows
        return self._load_pois_from_csv(city=city)

    def _load_pois_from_db(self, city: str) -> List[Dict[str, Any]]:
        if self.db is None or text is None:
            return []

        try:
            sql = text("""
                SELECT *
                FROM pois
                WHERE city = :city
                ORDER BY id ASC
            """)
            result = self.db.execute(sql, {"city": city})
            rows = [dict(r) for r in result.mappings().all()]
            return [self._normalize_poi_row(r) for r in rows]
        except Exception:
            # 兼容测试环境：数据库模型或表结构未就绪时直接降级 CSV
            return []

    def _load_pois_from_csv(self, city: str) -> List[Dict[str, Any]]:
        candidates = [
            Path("data/processed/chongqing_pois_enriched.csv"),
            Path("data/seed/chongqing_pois.csv"),
        ]

        for path in candidates:
            if path.exists():
                with path.open("r", encoding="utf-8-sig", newline="") as f:
                    rows = list(csv.DictReader(f))
                normalized = [self._normalize_poi_row(r) for r in rows]
                return [r for r in normalized if str(r.get("city")) == city]
        return []

    @staticmethod
    def _normalize_poi_row(row: Dict[str, Any]) -> Dict[str, Any]:
        def as_float(value: Any, default: float = 0.0) -> float:
            try:
                if value in {None, ""}:
                    return default
                return float(value)
            except Exception:
                return default

        def as_int(value: Any, default: int = 0) -> int:
            try:
                if value in {None, ""}:
                    return default
                return int(float(value))
            except Exception:
                return default

        return {
            "id": row.get("id"),
            "poi_name": row.get("poi_name") or row.get("name"),
            "poi_alias": row.get("poi_alias") or row.get("alias") or "",
            "city": row.get("city") or "重庆",
            "district": row.get("district") or "",
            "poi_type": row.get("poi_type") or "景点",
            "tags": row.get("tags") or "",
            "recommended_duration_minutes": as_int(row.get("recommended_duration_minutes"), 90),
            "best_time": row.get("best_time") or "全天",
            "avoid_time": row.get("avoid_time") or "",
            "price_level": row.get("price_level") or "low",
            "estimated_cost_low": as_int(row.get("estimated_cost_low"), 0),
            "estimated_cost_high": as_int(row.get("estimated_cost_high"), 0),
            "indoor_outdoor": row.get("indoor_outdoor") or "mixed",
            "suitable_for": row.get("suitable_for") or "",
            "avoid_tips": row.get("avoid_tips") or "",
            "nearby_area": row.get("nearby_area") or "未分组",
            "amap_poi_id": row.get("amap_poi_id") or "",
            "longitude": as_float(row.get("longitude")),
            "latitude": as_float(row.get("latitude")),
            "source": row.get("source") or "manual",
            "confidence": as_float(row.get("confidence"), 0.8),
            "match_status": row.get("match_status") or "matched",
        }
