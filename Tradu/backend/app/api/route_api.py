from fastapi import APIRouter, HTTPException

from backend.app.schemas.api_schema import RouteCalculateRequest
from backend.app.schemas.common_schema import ok
from backend.app.services.amap_http_service import AmapHttpService

router = APIRouter()


@router.post("/calculate")
def calculate_route(req: RouteCalculateRequest):
    try:
        data = AmapHttpService().route(
            origin=req.origin,
            destination=req.destination,
            mode=req.mode,
            city=req.city,
        )
        return ok(data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
