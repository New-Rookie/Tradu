from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.formal_itinerary_service import FormalItineraryService


def main():
    service = FormalItineraryService(db=None)
    request = {
        "destination": "重庆",
        "days": 3,
        "budget": 2500,
        "preferences": ["美食", "拍照", "夜景"],
        "avoid": ["高强度路线"],
        "travel_style": "relaxed",
        "walking_tolerance": "medium",
        "transport_preference": "public_transport",
    }
    weather = {"weather": "阴", "temperature": "30"}
    result = service.generate_itinerary(request, weather=weather)

    print(json.dumps(result, ensure_ascii=False, indent=2)[:4000])
    print("\n[SUMMARY]")
    print(f"plans: {len(result.get('plans', []))}")
    for plan in result.get("plans", []):
        days = plan.get("days", [])
        item_count = sum(len(day.get("items", [])) for day in days)
        print(
            f"{plan.get('plan_type')}: "
            f"{len(days)} days, {item_count} items, "
            f"score={plan.get('score')}, "
            f"cost={plan.get('total_estimated_cost_low')}-{plan.get('total_estimated_cost_high')}, "
            f"distance={plan.get('total_transport_distance_km')}km"
        )


if __name__ == "__main__":
    main()
