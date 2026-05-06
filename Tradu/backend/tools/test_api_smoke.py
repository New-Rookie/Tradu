import json
import requests

BASE_URL = "http://127.0.0.1:8000"


def pretty(title, data):
    print(f"\n[{title}]")
    print(json.dumps(data, ensure_ascii=False, indent=2)[:1200])


def assert_ok(resp):
    if resp.status_code >= 400:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")
    data = resp.json()
    if isinstance(data, dict) and "success" in data and not data["success"]:
        raise RuntimeError(f"API failed: {data}")
    return data


def main():
    r = requests.get(f"{BASE_URL}/health", timeout=10)
    pretty("health", assert_ok(r))

    r = requests.get(f"{BASE_URL}/api/v1/pois", params={"city": "重庆", "limit": 5}, timeout=10)
    pretty("pois", assert_ok(r))

    r = requests.post(
        f"{BASE_URL}/api/v1/itineraries/generate",
        json={
            "destination": "重庆",
            "days": 3,
            "budget": 2500,
            "preferences": ["美食", "拍照", "夜景"],
            "avoid": ["高强度路线"],
            "travel_style": "relaxed",
            "walking_tolerance": "medium",
            "transport_preference": "public_transport",
        },
        timeout=10,
    )
    pretty("itinerary", assert_ok(r))

    # 以下接口会真实调用外部服务。若网络或额度异常，可先注释。
    r = requests.get(f"{BASE_URL}/api/v1/weather", params={"city": "重庆"}, timeout=15)
    pretty("weather", assert_ok(r))

    print("\n[SUMMARY] API smoke test finished.")


if __name__ == "__main__":
    main()
