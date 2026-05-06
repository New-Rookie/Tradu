import argparse
import csv
import re
from pathlib import Path
from typing import Optional

from sqlalchemy import select

from backend.app.db.session import SessionLocal
from backend.app.models.poi import Poi


def split_to_list(value: Optional[str]) -> list[str]:
    if not value:
        return []
    return [x.strip() for x in re.split(r"[|,，、;；]", value) if x.strip()]


def to_int(value: Optional[str], default: int = 0) -> int:
    try:
        if value is None or str(value).strip() == "":
            return default
        return int(float(value))
    except Exception:
        return default


def to_float(value: Optional[str], default: Optional[float] = None) -> Optional[float]:
    try:
        if value is None or str(value).strip() == "":
            return default
        return float(value)
    except Exception:
        return default


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def upsert_poi(db, row: dict[str, str]) -> str:
    amap_poi_id = row.get("amap_poi_id", "").strip()
    poi_name = row.get("poi_name", "").strip()
    city = row.get("city", "重庆").strip() or "重庆"

    existing = None
    if amap_poi_id:
        existing = db.execute(select(Poi).where(Poi.amap_poi_id == amap_poi_id)).scalar_one_or_none()

    if existing is None:
        existing = db.execute(
            select(Poi).where(Poi.poi_name == poi_name, Poi.city == city)
        ).scalar_one_or_none()

    payload = {
        "poi_name": poi_name,
        "poi_alias": row.get("poi_alias", "").strip() or None,
        "city": city,
        "district": row.get("district", "").strip() or None,
        "poi_type": row.get("poi_type", "景点").strip() or "景点",
        "tags": split_to_list(row.get("tags")),
        "recommended_duration_minutes": to_int(row.get("recommended_duration_minutes"), 90),
        "best_time": row.get("best_time", "").strip() or None,
        "avoid_time": row.get("avoid_time", "").strip() or None,
        "price_level": row.get("price_level", "free").strip() or "free",
        "estimated_cost_low": to_int(row.get("estimated_cost_low"), 0),
        "estimated_cost_high": to_int(row.get("estimated_cost_high"), 0),
        "indoor_outdoor": row.get("indoor_outdoor", "mixed").strip() or "mixed",
        "suitable_for": split_to_list(row.get("suitable_for")),
        "avoid_tips": row.get("avoid_tips", "").strip() or None,
        "nearby_area": row.get("nearby_area", "").strip() or None,
        "amap_poi_id": amap_poi_id or None,
        "longitude": to_float(row.get("longitude")),
        "latitude": to_float(row.get("latitude")),
        "amap_name": row.get("amap_name", "").strip() or None,
        "amap_address": row.get("amap_address", "").strip() or None,
        "amap_type": row.get("amap_type", "").strip() or None,
        "amap_cityname": row.get("amap_cityname", "").strip() or None,
        "amap_adname": row.get("amap_adname", "").strip() or None,
        "match_score": to_int(row.get("match_score"), 0),
        "match_status": row.get("match_status", "not_found").strip() or "not_found",
        "match_keyword": row.get("match_keyword", "").strip() or None,
        "source": row.get("source", "manual").strip() or "manual",
        "confidence": to_float(row.get("confidence"), 0.8) or 0.8,
        "is_active": True,
    }

    if existing:
        for key, value in payload.items():
            setattr(existing, key, value)
        return "updated"

    db.add(Poi(**payload))
    return "inserted"


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed pois table from enriched Chongqing POI CSV.")
    parser.add_argument("--input", default="data/processed/chongqing_pois_enriched.csv")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"CSV not found: {input_path}")

    rows = read_csv(input_path)
    inserted = 0
    updated = 0

    with SessionLocal() as db:
        for row in rows:
            result = upsert_poi(db, row)
            if result == "inserted":
                inserted += 1
            else:
                updated += 1
        db.commit()

    print("[INFO] POI seed completed.")
    print(f"inserted: {inserted}")
    print(f"updated: {updated}")
    print(f"total: {len(rows)}")


if __name__ == "__main__":
    main()
