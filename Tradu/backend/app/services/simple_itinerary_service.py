import uuid
from typing import Dict, List

from backend.app.schemas.api_schema import ItineraryGenerateRequest
from backend.app.services.local_poi_service import LocalPoiService


class SimpleItineraryService:
    """
    V1 API 骨架阶段的临时行程生成器。
    后续第七/第八步会替换为正式评分和路线优化算法。
    """

    def __init__(self):
        self.poi_service = LocalPoiService()

    def generate(self, req: ItineraryGenerateRequest) -> Dict:
        pois = self.poi_service.list_pois(city=req.destination, limit=100)
        if req.imported_pois:
            imported_names = set(req.imported_pois)
            preferred = [p for p in pois if p["poi_name"] in imported_names]
            remaining = [p for p in pois if p["poi_name"] not in imported_names]
            pois = preferred + remaining

        # 简单规则：每天 4 个点位，轻松模式每天 3 个，高强度每天 6 个
        per_day = 4
        if req.travel_style == "relaxed":
            per_day = 3
        elif req.travel_style == "intensive":
            per_day = 6

        selected = pois[: max(req.days * per_day, per_day)]
        days = []
        cursor = 0
        for day_idx in range(1, req.days + 1):
            items = []
            for order, poi in enumerate(selected[cursor: cursor + per_day], start=1):
                items.append({
                    "sort_order": order,
                    "poi_name": poi["poi_name"],
                    "poi_type": poi.get("poi_type", ""),
                    "nearby_area": poi.get("nearby_area", ""),
                    "suggested_duration_minutes": poi.get("recommended_duration_minutes", 90),
                    "reason": "临时方案：根据本地 POI 顺序生成，后续将接入评分和路线优化。",
                })
            cursor += per_day
            days.append({
                "day_index": day_idx,
                "title": f"Day {day_idx} 重庆本地路线",
                "items": items,
            })

        return {
            "itinerary_id": f"temp_{uuid.uuid4().hex[:10]}",
            "destination": req.destination,
            "plans": [
                {
                    "plan_type": "综合最优方案",
                    "title": f"{req.destination}{req.days}日综合路线",
                    "summary": "当前为 API 骨架阶段临时方案，后续将接入正式评分、路线计算和 DeepSeek 解释。",
                    "days": days,
                    "estimated_cost_low": 0,
                    "estimated_cost_high": req.budget or 0,
                    "warnings": ["当前方案尚未进行交通路线优化。"],
                }
            ],
        }
