from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from backend.app.schemas.common_schema import ok
from backend.app.services.local_poi_service import LocalPoiService

router = APIRouter()


@router.get("")
def list_pois(
    city: str = "重庆",
    poi_type: Optional[str] = None,
    nearby_area: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
):
    data = LocalPoiService().list_pois(
        city=city,
        poi_type=poi_type,
        nearby_area=nearby_area,
        keyword=keyword,
        limit=limit,
    )
    return ok(data)


@router.get("/{poi_id}")
def get_poi(poi_id: int):
    poi = LocalPoiService().get_poi(poi_id)
    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")
    return ok(poi)
