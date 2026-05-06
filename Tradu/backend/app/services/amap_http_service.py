from typing import Dict
import requests

from backend.app.core.config import get_settings


class AmapHttpService:
    def __init__(self):
        self.settings = get_settings()
        if not self.settings.amap_web_service_key:
            raise RuntimeError("Missing AMAP_WEB_SERVICE_KEY in .env")
        self.base_url = self.settings.amap_web_service_base_url.rstrip("/")
        self.key = self.settings.amap_web_service_key

    def weather(self, city: str = "重庆") -> Dict:
        params = {
            "key": self.key,
            "city": city,
            "extensions": "base",
            "output": "JSON",
        }
        resp = requests.get(f"{self.base_url}/v3/weather/weatherInfo", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def route(self, origin: str, destination: str, mode: str = "walking", city: str = "重庆") -> Dict:
        if mode == "driving":
            endpoint = "/v3/direction/driving"
            params = {"origin": origin, "destination": destination}
        elif mode == "transit":
            endpoint = "/v3/direction/transit/integrated"
            params = {"origin": origin, "destination": destination, "city": city}
        else:
            endpoint = "/v3/direction/walking"
            params = {"origin": origin, "destination": destination}

        params.update({"key": self.key, "output": "JSON"})
        resp = requests.get(f"{self.base_url}{endpoint}", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
