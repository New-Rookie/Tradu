from collections import Counter

from sqlalchemy import select

from backend.app.db.session import SessionLocal
from backend.app.models.poi import Poi


def main() -> None:
    with SessionLocal() as db:
        pois = db.execute(select(Poi)).scalars().all()

    status_count = Counter(p.match_status for p in pois)
    area_count = Counter(p.nearby_area for p in pois)
    type_count = Counter(p.poi_type for p in pois)

    print("[SUMMARY]")
    print(f"total_pois: {len(pois)}")
    print(f"match_status: {dict(status_count)}")
    print(f"nearby_area_count: {dict(area_count)}")
    print(f"poi_type_count: {dict(type_count)}")

    print("\n[POIS]")
    for p in pois:
        print(f"{p.id}. {p.poi_name} | {p.district} | {p.poi_type} | {p.nearby_area} | {p.longitude},{p.latitude} | {p.match_status}")


if __name__ == "__main__":
    main()
