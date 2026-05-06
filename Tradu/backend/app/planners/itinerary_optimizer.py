from __future__ import annotations

import uuid
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from .distance_utils import (
    area_centers,
    area_distance_km,
    estimate_transport_minutes,
    estimate_walking_km,
    poi_distance_km,
)
from .plan_profiles import PLAN_PROFILES, TIME_PRIORITY, TRAVEL_STYLE_BASE_ITEMS, PlanProfile
from .scoring import score_poi, split_text_list


class ItineraryOptimizer:
    def __init__(self, pois: Sequence[Dict[str, Any]]):
        self.pois = [p for p in pois if self._is_valid_poi(p)]
        self.centers = area_centers(self.pois)

    @staticmethod
    def _is_valid_poi(poi: Dict[str, Any]) -> bool:
        if not poi.get("poi_name"):
            return False
        if poi.get("longitude") in {None, ""} or poi.get("latitude") in {None, ""}:
            return False
        return True

    def generate(self, user_request: Dict[str, Any], weather: Dict[str, Any] | None = None) -> Dict[str, Any]:
        days = max(1, min(int(user_request.get("days") or 1), 7))
        destination = user_request.get("destination") or user_request.get("city") or "重庆"

        plans = []
        for profile in PLAN_PROFILES:
            plan = self._generate_plan(profile, user_request, days, weather)
            plans.append(plan)

        return {
            "itinerary_id": f"formal_{uuid.uuid4().hex[:10]}",
            "destination": destination,
            "plans": plans,
        }

    def _generate_plan(
        self,
        profile: PlanProfile,
        user_request: Dict[str, Any],
        days: int,
        weather: Dict[str, Any] | None,
    ) -> Dict[str, Any]:
        travel_style = str(user_request.get("travel_style") or "standard")
        base_items = TRAVEL_STYLE_BASE_ITEMS.get(travel_style, 5)
        daily_limit = max(3, min(base_items + profile.daily_item_delta, 7))

        area_order = self._rank_areas(profile, user_request, weather)
        used_poi_names: set[str] = set()
        daily_routes = []

        for day_index in range(1, days + 1):
            main_area = area_order[(day_index - 1) % len(area_order)] if area_order else None
            candidate_areas = self._candidate_areas(main_area, profile.max_area_per_day)
            day_items = self._select_day_items(
                profile=profile,
                user_request=user_request,
                weather=weather,
                main_area=main_area,
                candidate_areas=candidate_areas,
                daily_limit=daily_limit,
                used_poi_names=used_poi_names,
            )

            # 如果当前片区点位不够，从全局高分候选补齐
            if len(day_items) < max(3, daily_limit - 1):
                day_items = self._fill_day_items(
                    current_items=day_items,
                    profile=profile,
                    user_request=user_request,
                    weather=weather,
                    daily_limit=daily_limit,
                    used_poi_names=used_poi_names,
                )

            sorted_items = self._sort_day_items(day_items)
            for item in sorted_items:
                used_poi_names.add(str(item.get("poi_name")))

            daily_routes.append(self._build_day_route(day_index, main_area, sorted_items, user_request))

        plan_totals = self._summarize_plan(daily_routes)
        plan_score = self._plan_score(daily_routes)

        return {
            "plan_type": profile.plan_type,
            "title": f"{user_request.get('destination', '重庆')}{days}日{profile.title_suffix}",
            "summary": self._build_plan_summary(profile, daily_routes),
            "score": plan_score,
            "total_estimated_cost_low": plan_totals["cost_low"],
            "total_estimated_cost_high": plan_totals["cost_high"],
            "total_transport_distance_km": plan_totals["transport_distance_km"],
            "total_walking_distance_km": plan_totals["walking_distance_km"],
            "total_transport_time_minutes": plan_totals["transport_time_minutes"],
            "days": daily_routes,
        }

    def _rank_areas(self, profile: PlanProfile, user_request: Dict[str, Any], weather: Dict[str, Any] | None) -> List[str]:
        grouped = defaultdict(list)
        for poi in self.pois:
            grouped[str(poi.get("nearby_area") or "未分组")].append(poi)

        area_scores = []
        for area, pois in grouped.items():
            scores = [score_poi(p, user_request, profile, main_area=area, weather=weather) for p in pois]
            # 数量和均分都考虑，避免只有一个点的片区过高
            final_score = (sum(scores) / len(scores)) * 0.75 + min(len(pois) * 5, 25)
            area_scores.append((area, final_score))

        area_scores.sort(key=lambda x: x[1], reverse=True)
        return [area for area, _ in area_scores]

    def _candidate_areas(self, main_area: str | None, max_area_count: int) -> List[str]:
        if not main_area:
            return []
        if max_area_count <= 1:
            return [main_area]

        distances = []
        for area in self.centers.keys():
            distances.append((area, area_distance_km(main_area, area, self.centers)))
        distances.sort(key=lambda x: x[1])
        return [area for area, _ in distances[:max_area_count]]

    def _select_day_items(
        self,
        profile: PlanProfile,
        user_request: Dict[str, Any],
        weather: Dict[str, Any] | None,
        main_area: str | None,
        candidate_areas: List[str],
        daily_limit: int,
        used_poi_names: set[str],
    ) -> List[Dict[str, Any]]:
        candidates = []
        for poi in self.pois:
            name = str(poi.get("poi_name"))
            if name in used_poi_names:
                continue
            if candidate_areas and poi.get("nearby_area") not in candidate_areas:
                continue

            s = score_poi(poi, user_request, profile, main_area=main_area, weather=weather)
            item = dict(poi)
            item["score"] = s
            candidates.append(item)

        candidates.sort(key=lambda x: x["score"], reverse=True)
        return self._pick_balanced_items(candidates, daily_limit, profile)

    def _fill_day_items(
        self,
        current_items: List[Dict[str, Any]],
        profile: PlanProfile,
        user_request: Dict[str, Any],
        weather: Dict[str, Any] | None,
        daily_limit: int,
        used_poi_names: set[str],
    ) -> List[Dict[str, Any]]:
        current_names = {str(x.get("poi_name")) for x in current_items}
        candidates = []
        for poi in self.pois:
            name = str(poi.get("poi_name"))
            if name in used_poi_names or name in current_names:
                continue
            s = score_poi(poi, user_request, profile, weather=weather)
            item = dict(poi)
            item["score"] = s
            candidates.append(item)
        candidates.sort(key=lambda x: x["score"], reverse=True)

        merged = list(current_items)
        for item in candidates:
            if len(merged) >= daily_limit:
                break
            merged.append(item)
        return self._pick_balanced_items(merged, daily_limit, profile)

    def _pick_balanced_items(self, candidates: List[Dict[str, Any]], limit: int, profile: PlanProfile) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        selected: List[Dict[str, Any]] = []
        type_counter: Counter[str] = Counter()

        # 美食方案需要保证餐饮/商圈点，其他方案也尽量保留一个餐饮点
        if profile.plan_type == "美食体验方案":
            food_candidates = [c for c in candidates if c.get("poi_type") in {"餐饮", "商圈"}]
            for c in food_candidates[:2]:
                selected.append(c)
                type_counter[str(c.get("poi_type"))] += 1
        else:
            food_candidates = [c for c in candidates if c.get("poi_type") == "餐饮"]
            if food_candidates:
                c = food_candidates[0]
                selected.append(c)
                type_counter[str(c.get("poi_type"))] += 1

        for c in candidates:
            if len(selected) >= limit:
                break
            if c in selected:
                continue
            poi_type = str(c.get("poi_type") or "")

            # 避免同一天餐饮过多，除非是美食方案
            if profile.plan_type != "美食体验方案" and poi_type == "餐饮" and type_counter[poi_type] >= 1:
                continue
            if type_counter[poi_type] >= 3:
                continue

            selected.append(c)
            type_counter[poi_type] += 1

        return selected[:limit]

    def _sort_day_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not items:
            return []

        def time_key(poi: Dict[str, Any]) -> int:
            best_time = str(poi.get("best_time") or "全天")
            if "上午" in best_time:
                return TIME_PRIORITY["上午"]
            if "中午" in best_time:
                return TIME_PRIORITY["中午"]
            if "下午" in best_time:
                return TIME_PRIORITY["下午"]
            if "晚上" in best_time:
                return TIME_PRIORITY["晚上"]
            return TIME_PRIORITY["全天"]

        # 先按时间段粗排
        remaining = sorted(items, key=time_key)
        ordered = [remaining.pop(0)]

        # 相同/相近时间段用最近邻减少折返
        while remaining:
            last = ordered[-1]
            next_idx = min(range(len(remaining)), key=lambda i: poi_distance_km(last, remaining[i]))
            ordered.append(remaining.pop(next_idx))

        return ordered

    def _build_day_route(
        self,
        day_index: int,
        main_area: str | None,
        items: List[Dict[str, Any]],
        user_request: Dict[str, Any],
    ) -> Dict[str, Any]:
        transport_preference = str(user_request.get("transport_preference") or "public_transport")
        route_items = []
        total_cost_low = 0
        total_cost_high = 0
        total_transport_distance = 0.0
        total_walking_distance = 0.0
        total_transport_time = 0

        for idx, poi in enumerate(items):
            cost_low = int(float(poi.get("estimated_cost_low") or 0))
            cost_high = int(float(poi.get("estimated_cost_high") or 0))
            total_cost_low += cost_low
            total_cost_high += cost_high

            distance_to_next = 0.0
            walking_to_next = 0.0
            time_to_next = 0
            transport_to_next = ""
            if idx < len(items) - 1:
                distance_to_next = poi_distance_km(poi, items[idx + 1])
                walking_to_next = estimate_walking_km(distance_to_next, transport_preference)
                time_to_next = estimate_transport_minutes(distance_to_next, transport_preference)
                total_transport_distance += distance_to_next
                total_walking_distance += walking_to_next
                total_transport_time += time_to_next
                transport_to_next = self._suggest_transport(distance_to_next, transport_preference)

            route_items.append({
                "sort_order": idx + 1,
                "poi_id": poi.get("id"),
                "poi_name": poi.get("poi_name"),
                "poi_type": poi.get("poi_type"),
                "nearby_area": poi.get("nearby_area"),
                "longitude": poi.get("longitude"),
                "latitude": poi.get("latitude"),
                "tags": split_text_list(poi.get("tags")),
                "suggested_duration_minutes": int(float(poi.get("recommended_duration_minutes") or 90)),
                "best_time": poi.get("best_time"),
                "estimated_cost_low": cost_low,
                "estimated_cost_high": cost_high,
                "distance_to_next_km": round(distance_to_next, 2),
                "walking_to_next_km": walking_to_next,
                "time_to_next_minutes": time_to_next,
                "transport_to_next": transport_to_next,
                "score": round(float(poi.get("score") or 0), 2),
                "reason": self._item_reason(poi),
                "tips": poi.get("avoid_tips") or "",
            })

        return {
            "day_index": day_index,
            "title": f"Day {day_index} {main_area or '重庆本地'}路线",
            "summary": self._day_summary(main_area, route_items),
            "main_area": main_area,
            "estimated_cost_low": total_cost_low,
            "estimated_cost_high": total_cost_high,
            "transport_distance_km": round(total_transport_distance, 2),
            "walking_distance_km": round(total_walking_distance, 2),
            "transport_time_minutes": total_transport_time,
            "items": route_items,
        }

    @staticmethod
    def _suggest_transport(distance_km: float, transport_preference: str) -> str:
        if distance_km <= 1.2 or transport_preference == "walking":
            return "步行"
        if transport_preference == "taxi":
            return "打车"
        return "公共交通/打车"

    @staticmethod
    def _item_reason(poi: Dict[str, Any]) -> str:
        tags = split_text_list(poi.get("tags"))[:3]
        tag_text = "、".join(tags) if tags else "本地推荐"
        area = poi.get("nearby_area") or "附近片区"
        return f"该点位位于{area}，标签为{tag_text}，适合并入当天路线。"

    @staticmethod
    def _day_summary(main_area: str | None, items: List[Dict[str, Any]]) -> str:
        if not items:
            return "当天没有可用点位。"
        names = "、".join([str(x.get("poi_name")) for x in items[:4]])
        return f"当天以{main_area or '核心片区'}为主，安排{name_or_empty(names)}等点位，减少无效折返。"

    @staticmethod
    def _summarize_plan(daily_routes: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "cost_low": sum(int(d.get("estimated_cost_low") or 0) for d in daily_routes),
            "cost_high": sum(int(d.get("estimated_cost_high") or 0) for d in daily_routes),
            "transport_distance_km": round(sum(float(d.get("transport_distance_km") or 0) for d in daily_routes), 2),
            "walking_distance_km": round(sum(float(d.get("walking_distance_km") or 0) for d in daily_routes), 2),
            "transport_time_minutes": sum(int(d.get("transport_time_minutes") or 0) for d in daily_routes),
        }

    @staticmethod
    def _plan_score(daily_routes: List[Dict[str, Any]]) -> float:
        scores = []
        for day in daily_routes:
            for item in day.get("items", []):
                scores.append(float(item.get("score") or 0))
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 2)

    @staticmethod
    def _build_plan_summary(profile: PlanProfile, daily_routes: List[Dict[str, Any]]) -> str:
        areas = [d.get("main_area") for d in daily_routes if d.get("main_area")]
        area_text = "、".join(areas[:3]) if areas else "重庆核心片区"
        return f"{profile.summary_focus} 本方案主要覆盖{area_text}，适合希望路线清晰、点位可执行的用户。"


def name_or_empty(text: str) -> str:
    return text or "核心"
