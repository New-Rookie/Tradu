from fastapi import APIRouter

from backend.app.schemas.api_schema import ItineraryGenerateRequest
from backend.app.schemas.common_schema import ok
from backend.app.services.formal_itinerary_service import FormalItineraryService

router = APIRouter()


@router.post("/generate")
def generate_itinerary(req: ItineraryGenerateRequest):
    data = FormalItineraryService().generate_itinerary(req)
    return ok(data)


@router.get("/{itinerary_id}")
def get_itinerary(itinerary_id: str):
    return ok({
        "itinerary_id": itinerary_id,
        "status": "placeholder",
        "message": "V1 API skeleton: persistent itinerary storage will be implemented in later steps.",
    })
