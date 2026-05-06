from __future__ import annotations

import json
import requests


BASE_URL = "http://127.0.0.1:8000"


def main():
    payload = {
        "destination": "重庆",
        "days": 3,
        "budget": 2500,
        "preferences": ["美食", "拍照", "夜景"],
        "avoid": ["高强度路线"],
        "travel_style": "relaxed",
        "walking_tolerance": "medium",
        "transport_preference": "public_transport",
    }

    resp = requests.post(f"{BASE_URL}/api/v1/itineraries/generate", json=payload, timeout=60)
    print(f"status_code={resp.status_code}")
    data = resp.json()
    print(json.dumps(data, ensure_ascii=False, indent=2)[:5000])

    result = data.get("data") if isinstance(data, dict) else None
    plans = (result or {}).get("plans", [])

    print("\n[SUMMARY]")
    print(f"plans: {len(plans)}")
    for plan in plans:
        print(f"{plan.get('plan_type')}: {len(plan.get('days', []))} days, score={plan.get('score')}")


if __name__ == "__main__":
    main()
