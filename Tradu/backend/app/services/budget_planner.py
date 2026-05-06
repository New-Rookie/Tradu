from __future__ import annotations

from typing import Any, Dict, List


class BudgetPlanner:
    """预算约束估算器：不承诺实时价格，仅用于路线约束与风险提示。"""

    def create_budget_plan(self, total_budget: float | int | None, days: int, travel_style: str = "standard") -> Dict[str, Any]:
        total = max(float(total_budget or 0), 0.0)
        days = max(int(days or 1), 1)
        per_day = total / days if days else total
        if per_day < 500:
            warning = "budget_tight"
            ratios = {"accommodation": 0.34, "food": 0.25, "attraction": 0.10, "transport": 0.16, "buffer": 0.15}
        elif per_day > 1200:
            warning = "budget_flexible"
            ratios = {"accommodation": 0.40, "food": 0.23, "attraction": 0.12, "transport": 0.10, "buffer": 0.15}
        else:
            warning = "budget_normal"
            ratios = {"accommodation": 0.36, "food": 0.24, "attraction": 0.12, "transport": 0.12, "buffer": 0.16}
        if travel_style in {"relaxed", "comfort"}:
            ratios["transport"] += 0.03
            ratios["attraction"] = max(0.08, ratios["attraction"] - 0.02)
            ratios["food"] = max(0.20, ratios["food"] - 0.01)
        plan = {
            "total_budget": round(total, 2),
            "days": days,
            "accommodation_budget": round(total * ratios["accommodation"], 2),
            "food_budget": round(total * ratios["food"], 2),
            "attraction_budget": round(total * ratios["attraction"], 2),
            "transport_budget": round(total * ratios["transport"], 2),
            "buffer_budget": round(total * ratios["buffer"], 2),
            "daily_food_budget": round(total * ratios["food"] / days, 2),
            "daily_transport_budget": round(total * ratios["transport"] / days, 2),
            "budget_warning": warning,
            "budget_control_hint": "预算约束估算，酒店/餐饮/门票价格会随日期和现场情况波动。",
        }
        return plan

    def estimate_daily_food_budget(self, days: int, travel_style: str = "standard") -> float:
        base = 160 if travel_style in {"relaxed", "foodie"} else 120
        return round(base * max(days, 1), 2)

    def estimate_daily_transport_budget(self, days: int, transport_preference: str = "public_transport") -> float:
        per_day = 60 if transport_preference == "taxi" else 35
        return round(per_day * max(days, 1), 2)

    def check_plan_budget(self, itinerary: Dict[str, Any], budget_plan: Dict[str, Any]) -> Dict[str, Any]:
        high = float(itinerary.get("total_estimated_cost_high") or itinerary.get("estimated_cost_high") or 0)
        cap = float(budget_plan.get("attraction_budget") or 0) + float(budget_plan.get("food_budget") or 0) + float(budget_plan.get("transport_budget") or 0)
        return {"estimated_in_route_cost_high": high, "route_budget_cap": round(cap, 2), "within_route_budget": high <= cap if cap else True}

    def generate_budget_warnings(self, itinerary: Dict[str, Any], budget_plan: Dict[str, Any]) -> List[str]:
        warnings = [budget_plan.get("budget_warning", "budget_normal")]
        check = self.check_plan_budget(itinerary, budget_plan)
        if not check.get("within_route_budget"):
            warnings.append("route_estimate_may_exceed_budget")
        if float(budget_plan.get("buffer_budget") or 0) < float(budget_plan.get("total_budget") or 0) * 0.1:
            warnings.append("buffer_too_low")
        return [w for w in warnings if w]
