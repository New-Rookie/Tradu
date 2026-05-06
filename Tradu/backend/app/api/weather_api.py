from fastapi import APIRouter, HTTPException

from backend.app.schemas.common_schema import ok
from backend.app.services.amap_http_service import AmapHttpService

router = APIRouter()


@router.get("")
def query_weather(city: str = "重庆"):
    try:
        data = AmapHttpService().weather(city=city)
        return ok(data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
