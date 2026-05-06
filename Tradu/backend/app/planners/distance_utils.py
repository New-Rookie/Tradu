from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Optional, Tuple


EARTH_RADIUS_KM = 6371.0088


def _to_float(value: Any) -> Optional[float]:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def get_lon_lat(poi: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    lon = _to_float(poi.get("longitude"))
    lat = _to_float(poi.get("latitude"))
    return lon, lat


def haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    lon1_rad = math.radians(lon1)
    lat1_rad = math.radians(lat1)
    lon2_rad = math.radians(lon2)
    lat2_rad = math.radians(lat2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def poi_distance_km(poi_a: Dict[str, Any], poi_b: Dict[str, Any]) -> float:
    lon1, lat1 = get_lon_lat(poi_a)
    lon2, lat2 = get_lon_lat(poi_b)
    if lon1 is None or lat1 is None or lon2 is None or lat2 is None:
        return 999.0
    return haversine_km(lon1, lat1, lon2, lat2)


def estimate_transport_minutes(distance_km: float, transport_preference: str = "public_transport") -> int:
    """
    粗略估算，不等价于高德实际路线时间。
    第九步会接入高德路线详情替换这里。
    """
    if distance_km <= 0:
        return 0

    if distance_km <= 1.2:
        speed_kmh = 4.2  # walking
        buffer = 3
    elif transport_preference == "taxi":
        speed_kmh = 22
        buffer = 8
    elif transport_preference == "walking":
        speed_kmh = 4.2
        buffer = 2
    else:
        speed_kmh = 16  # public transport approximation
        buffer = 10

    return int(round(distance_km / speed_kmh * 60 + buffer))


def estimate_walking_km(distance_km: float, transport_preference: str = "public_transport") -> float:
    if distance_km <= 1.2:
        return round(distance_km, 2)
    if transport_preference == "walking":
        return round(distance_km, 2)
    return round(min(distance_km * 0.25, 1.2), 2)


def area_centers(pois: Iterable[Dict[str, Any]]) -> Dict[str, Tuple[float, float]]:
    tmp: Dict[str, List[Tuple[float, float]]] = {}
    for poi in pois:
        area = str(poi.get("nearby_area") or "未分组")
        lon, lat = get_lon_lat(poi)
        if lon is None or lat is None:
            continue
        tmp.setdefault(area, []).append((lon, lat))

    centers: Dict[str, Tuple[float, float]] = {}
    for area, points in tmp.items():
        if not points:
            continue
        centers[area] = (
            sum(p[0] for p in points) / len(points),
            sum(p[1] for p in points) / len(points),
        )
    return centers


def area_distance_km(area_a: str, area_b: str, centers: Dict[str, Tuple[float, float]]) -> float:
    if area_a == area_b:
        return 0.0
    if area_a not in centers or area_b not in centers:
        return 999.0
    lon1, lat1 = centers[area_a]
    lon2, lat2 = centers[area_b]
    return haversine_km(lon1, lat1, lon2, lat2)
