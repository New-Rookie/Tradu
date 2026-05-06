import csv
from pathlib import Path
from typing import Dict, List, Optional

from backend.app.core.config import get_settings


def _split_tags(value: str) -> List[str]:
    if not value:
        return []
    return [x.strip() for x in value.replace(",", "|").split("|") if x.strip()]


def _safe_float(value: str) -> Optional[float]:
    try:
        if value is None or str(value).strip() == "":
            return None
        return float(value)
    except Exception:
        return None


class LocalPoiService:
    def __init__(self, csv_path: Optional[str] = None):
        settings = get_settings()
        self.csv_path = Path(csv_path or settings.local_poi_csv)

    def list_pois(
        self,
        city: str = "重庆",
        poi_type: Optional[str] = None,
        nearby_area: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        if not self.csv_path.exists():
            return []

        with self.csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))

        result = []
        for idx, row in enumerate(rows, start=1):
            if city and row.get("city") != city:
                continue
            if poi_type and row.get("poi_type") != poi_type:
                continue
            if nearby_area and row.get("nearby_area") != nearby_area:
                continue
            if keyword:
                search_text = " ".join([
                    row.get("poi_name", ""),
                    row.get("poi_alias", ""),
                    row.get("tags", ""),
                    row.get("nearby_area", ""),
                ])
                if keyword not in search_text:
                    continue

            result.append({
                "id": idx,
                "poi_name": row.get("poi_name", ""),
                "city": row.get("city", ""),
                "district": row.get("district", ""),
                "poi_type": row.get("poi_type", ""),
                "tags": _split_tags(row.get("tags", "")),
                "nearby_area": row.get("nearby_area", ""),
                "longitude": _safe_float(row.get("longitude", "")),
                "latitude": _safe_float(row.get("latitude", "")),
                "amap_poi_id": row.get("amap_poi_id", ""),
                "recommended_duration_minutes": int(float(row.get("recommended_duration_minutes") or 90)),
                "best_time": row.get("best_time", ""),
                "price_level": row.get("price_level", ""),
                "indoor_outdoor": row.get("indoor_outdoor", ""),
                "avoid_tips": row.get("avoid_tips", ""),
                "match_status": row.get("match_status", ""),
            })

            if len(result) >= limit:
                break

        return result

    def get_poi(self, poi_id: int) -> Optional[Dict]:
        pois = self.list_pois(limit=10000)
        for poi in pois:
            if poi["id"] == poi_id:
                return poi
        return None
