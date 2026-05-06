from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.service_poi import ServicePoi
from backend.app.schemas.api_schema import ServicePoiRefreshRequest
from backend.app.schemas.common_schema import ok
from backend.app.services.amap_service_poi_fetcher import AMapServicePoiFetcher

router = APIRouter()


@router.get("")
def list_service_pois(city: str = "重庆", service_type: str | None = None, nearby_area: str | None = None, limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    stmt = select(ServicePoi).where(ServicePoi.city == city)
    if service_type:
        stmt = stmt.where(ServicePoi.service_type == service_type)
    if nearby_area:
        stmt = stmt.where(ServicePoi.nearby_area == nearby_area)
    rows = db.execute(stmt.limit(limit)).scalars().all()
    data = [{"id": r.id, "amap_poi_id": r.amap_poi_id, "name": r.name, "city": r.city, "district": r.district, "nearby_area": r.nearby_area, "address": r.address, "longitude": r.longitude, "latitude": r.latitude, "service_type": r.service_type, "poi_type": r.poi_type, "tags": r.tags or [], "rating": r.rating, "cost": r.cost, "price_level": r.price_level, "business_area": r.business_area, "source": r.source} for r in rows]
    return ok(data)


@router.post("/refresh")
def refresh_service_pois(req: ServicePoiRefreshRequest, db: Session = Depends(get_db)):
    result = AMapServicePoiFetcher(db).refresh_area_service_pois(req.city, req.nearby_area, service_types=req.service_types)
    return ok({"success": True, **result})
