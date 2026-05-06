from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class PlanProfile:
    plan_type: str
    title_suffix: str
    summary_focus: str
    weights: Dict[str, float]
    preferred_tags: List[str] = field(default_factory=list)
    preferred_types: List[str] = field(default_factory=list)
    avoid_types: List[str] = field(default_factory=list)
    daily_item_delta: int = 0
    max_area_per_day: int = 2


PLAN_PROFILES: List[PlanProfile] = [
    PlanProfile(
        plan_type="综合最优方案",
        title_suffix="综合最优路线",
        summary_focus="在偏好匹配、路线便利、预算和经典程度之间保持均衡。",
        weights={
            "preference": 0.30,
            "geo": 0.20,
            "budget": 0.15,
            "content": 0.15,
            "time": 0.10,
            "weather": 0.10,
        },
        preferred_tags=[],
        preferred_types=[],
        daily_item_delta=0,
    ),
    PlanProfile(
        plan_type="低预算方案",
        title_suffix="低预算路线",
        summary_focus="优先选择免费、低消费和片区集中的点位，控制总体支出。",
        weights={
            "preference": 0.22,
            "geo": 0.18,
            "budget": 0.32,
            "content": 0.12,
            "time": 0.08,
            "weather": 0.08,
        },
        preferred_tags=["低预算", "免费", "小吃"],
        daily_item_delta=0,
    ),
    PlanProfile(
        plan_type="少走路轻松方案",
        title_suffix="少走路轻松路线",
        summary_focus="优先安排同片区点位，降低跨区移动和步行压力。",
        weights={
            "preference": 0.22,
            "geo": 0.34,
            "budget": 0.14,
            "content": 0.10,
            "time": 0.10,
            "weather": 0.10,
        },
        preferred_tags=["轻松", "交通便利", "室内"],
        preferred_types=["商圈", "餐饮", "博物馆", "亲子"],
        daily_item_delta=-1,
        max_area_per_day=1,
    ),
    PlanProfile(
        plan_type="美食体验方案",
        title_suffix="美食体验路线",
        summary_focus="提高美食、夜市和商圈的优先级，适合以吃逛为核心的旅行。",
        weights={
            "preference": 0.34,
            "geo": 0.18,
            "budget": 0.12,
            "content": 0.18,
            "time": 0.08,
            "weather": 0.10,
        },
        preferred_tags=["美食", "小吃", "夜市"],
        preferred_types=["餐饮", "商圈"],
        daily_item_delta=0,
    ),
    PlanProfile(
        plan_type="经典打卡方案",
        title_suffix="经典打卡路线",
        summary_focus="优先覆盖地标、经典景点、夜景和热门拍照点。",
        weights={
            "preference": 0.28,
            "geo": 0.16,
            "budget": 0.10,
            "content": 0.26,
            "time": 0.10,
            "weather": 0.10,
        },
        preferred_tags=["经典打卡", "夜景", "拍照", "地标"],
        preferred_types=["景点", "夜景", "拍照点", "人文景点"],
        daily_item_delta=1,
    ),
]


TRAVEL_STYLE_BASE_ITEMS = {
    "relaxed": 4,
    "standard": 5,
    "intensive": 6,
}


TIME_PRIORITY = {
    "上午": 1,
    "中午": 2,
    "下午": 3,
    "全天": 3,
    "晚上": 5,
}
