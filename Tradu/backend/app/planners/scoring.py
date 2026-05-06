from __future__ import annotations

from typing import Any, Dict, Iterable, List, Sequence, Set

from .plan_profiles import PlanProfile


def split_text_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    text = str(value).strip()
    if not text:
        return []
    for sep in ["|", ",", "，", "/", "、", ";", "；"]:
        text = text.replace(sep, "|")
    return [x.strip() for x in text.split("|") if x.strip()]


def normalize_set(values: Iterable[str]) -> Set[str]:
    return {str(v).strip().lower() for v in values if str(v).strip()}


def price_level_to_score(price_level: str, budget: float, days: int) -> float:
    level = (price_level or "").lower()
    per_day_budget = budget / max(days, 1) if budget else 0

    base = {
        "free": 100,
        "low": 88,
        "medium": 68,
        "high": 45,
    }.get(level, 60)

    if per_day_budget >= 1000:
        return min(base + 10, 100)
    if per_day_budget >= 600:
        return base
    if per_day_budget >= 300:
        penalty = {"high": 35, "medium": 10}.get(level, 0)
        return max(base - penalty, 0)
    penalty = {"high": 50, "medium": 22, "low": 0, "free": 0}.get(level, 8)
    return max(base - penalty, 0)


def preference_score(poi: Dict[str, Any], user_preferences: Sequence[str], profile: PlanProfile) -> float:
    poi_tags = normalize_set(split_text_list(poi.get("tags")))
    poi_type = str(poi.get("poi_type") or "").strip().lower()
    user_pref = normalize_set(user_preferences)
    profile_tags = normalize_set(profile.preferred_tags)
    profile_types = normalize_set(profile.preferred_types)

    score = 45.0

    if user_pref:
        matched = len(poi_tags & user_pref)
        score += min(matched * 18, 45)

        # 用户偏好可能直接对应类型，如“美食”“拍照”“夜景”
        for pref in user_pref:
            if pref in poi_type:
                score += 16
                break
    else:
        score += 10

    profile_match = len(poi_tags & profile_tags)
    score += min(profile_match * 12, 30)

    if poi_type in profile_types:
        score += 20

    return max(0, min(score, 100))


def geo_score(poi: Dict[str, Any], main_area: str | None = None) -> float:
    if not main_area:
        return 70.0
    return 100.0 if poi.get("nearby_area") == main_area else 60.0


def content_score(poi: Dict[str, Any], profile: PlanProfile) -> float:
    confidence = poi.get("confidence")
    try:
        conf_score = float(confidence) * 100
    except Exception:
        conf_score = 75.0

    tags = normalize_set(split_text_list(poi.get("tags")))
    bonus = 0
    if "经典打卡" in tags or "classic" in tags:
        bonus += 8
    if "拍照" in tags:
        bonus += 5
    if "人多" in tags and profile.plan_type == "少走路轻松方案":
        bonus -= 8

    if str(poi.get("match_status") or "") not in {"matched", "manual_verified"}:
        bonus -= 12

    return max(0, min(conf_score + bonus, 100))


def time_score(poi: Dict[str, Any], preferred_slot: str | None = None) -> float:
    best_time = str(poi.get("best_time") or "全天")
    if not preferred_slot:
        return 75.0
    if preferred_slot in best_time or "全天" in best_time:
        return 95.0
    if preferred_slot == "晚上" and "下午" in best_time:
        return 70.0
    if preferred_slot == "上午" and "下午" in best_time:
        return 65.0
    return 55.0


def weather_score(poi: Dict[str, Any], weather: Dict[str, Any] | None) -> float:
    if not weather:
        return 75.0

    weather_text = str(weather.get("weather") or weather.get("text") or "")
    temp_text = str(weather.get("temperature") or "")
    indoor_outdoor = str(poi.get("indoor_outdoor") or "").lower()
    poi_type = str(poi.get("poi_type") or "")

    try:
        temp = float(temp_text)
    except Exception:
        temp = None

    score = 75.0

    if any(x in weather_text for x in ["雨", "雪", "雷", "暴"]):
        if indoor_outdoor == "outdoor":
            score -= 30
        elif indoor_outdoor == "indoor":
            score += 18
        if poi_type in {"博物馆", "商圈", "餐饮", "亲子"}:
            score += 12

    if temp is not None and temp >= 34:
        if indoor_outdoor == "outdoor":
            score -= 20
        if indoor_outdoor == "indoor":
            score += 10

    if temp is not None and temp <= 6:
        if "夜景" in poi_type or indoor_outdoor == "outdoor":
            score -= 12

    return max(0, min(score, 100))


def avoid_penalty(poi: Dict[str, Any], avoid: Sequence[str]) -> float:
    if not avoid:
        return 0.0

    avoid_set = normalize_set(avoid)
    tags = normalize_set(split_text_list(poi.get("tags")))
    tips = str(poi.get("avoid_tips") or "").lower()
    poi_type = str(poi.get("poi_type") or "").lower()

    penalty = 0.0
    for item in avoid_set:
        if item in tags or item in poi_type or item in tips:
            penalty += 18
        if "高强度" in item and ("citywalk" in poi_type or "步行" in tags):
            penalty += 10
        if "排队" in item and ("人多" in tags or "排队" in tips):
            penalty += 15
    return min(penalty, 45)


def score_poi(
    poi: Dict[str, Any],
    user_request: Dict[str, Any],
    profile: PlanProfile,
    main_area: str | None = None,
    preferred_slot: str | None = None,
    weather: Dict[str, Any] | None = None,
) -> float:
    days = int(user_request.get("days") or 1)
    budget = float(user_request.get("budget") or 0)
    preferences = split_text_list(user_request.get("preferences"))
    avoid = split_text_list(user_request.get("avoid"))

    sub_scores = {
        "preference": preference_score(poi, preferences, profile),
        "geo": geo_score(poi, main_area),
        "budget": price_level_to_score(str(poi.get("price_level") or ""), budget, days),
        "content": content_score(poi, profile),
        "time": time_score(poi, preferred_slot),
        "weather": weather_score(poi, weather),
    }

    weighted = 0.0
    for key, weight in profile.weights.items():
        weighted += sub_scores.get(key, 0) * weight

    weighted -= avoid_penalty(poi, avoid)

    if str(poi.get("poi_type") or "").lower() in normalize_set(profile.avoid_types):
        weighted -= 20

    return round(max(0, min(weighted, 100)), 2)
