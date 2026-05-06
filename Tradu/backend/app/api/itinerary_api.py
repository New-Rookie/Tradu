from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.api_schema import (
    CompressDayRequest,
    ContinueFromLocationRequest,
    ItineraryAdjustRequest,
    ItineraryGenerateRequest,
    RemovePoiRequest,
    SessionOnlyRequest,
)
from backend.app.schemas.common_schema import ok
from backend.app.services.formal_itinerary_service import FormalItineraryService
from backend.app.services.itinerary_adjustment_service import ItineraryAdjustmentService
from backend.app.services.itinerary_state_service import ItineraryStateService

router = APIRouter()


@router.post("/generate")
def generate_itinerary(req: ItineraryGenerateRequest, db: Session = Depends(get_db)):
    data = FormalItineraryService(db).generate_itinerary(req)
    if req.session_id:
        ItineraryStateService(db).create_or_update_state(req.session_id, data, req.model_dump())
    return ok(data)


@router.post("/adjust")
def adjust_itinerary(req: ItineraryAdjustRequest, db: Session = Depends(get_db)):
    data = ItineraryAdjustmentService(db).adjust_by_instruction(req.session_id, req.instruction)
    return ok({"success": True, "data": data})


@router.post("/reduce-walking")
def reduce_walking(req: SessionOnlyRequest, db: Session = Depends(get_db)):
    data = ItineraryAdjustmentService(db).regenerate_after_state_action(req.session_id, "reduce_walking")
    return ok({"success": True, "data": data})


@router.post("/rain-mode")
def rain_mode(req: SessionOnlyRequest, db: Session = Depends(get_db)):
    data = ItineraryAdjustmentService(db).regenerate_after_state_action(req.session_id, "rain_mode")
    return ok({"success": True, "data": data})


@router.post("/remove-poi")
def remove_poi(req: RemovePoiRequest, db: Session = Depends(get_db)):
    data = ItineraryAdjustmentService(db).regenerate_after_state_action(req.session_id, "remove_poi", poi_name=req.poi_name)
    return ok({"success": True, "data": data})


@router.post("/compress-day")
def compress_day(req: CompressDayRequest, db: Session = Depends(get_db)):
    data = ItineraryAdjustmentService(db).regenerate_after_state_action(req.session_id, "compress_day", day_index=req.day_index)
    return ok({"success": True, "data": data})


@router.post("/continue-from-location")
def continue_from_location(req: ContinueFromLocationRequest, db: Session = Depends(get_db)):
    data = ItineraryAdjustmentService(db).regenerate_after_state_action(req.session_id, "continue_from_current_location", longitude=req.longitude, latitude=req.latitude, current_time=req.current_time)
    return ok({"success": True, "data": data})


@router.get("/state/{session_id}")
def get_itinerary_state(session_id: str, db: Session = Depends(get_db)):
    state = ItineraryStateService(db).get_state(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="itinerary state not found")
    return ok(ItineraryStateService(db).to_dict(state))


@router.get("/{itinerary_id}")
def get_itinerary(itinerary_id: str):
    return ok({"itinerary_id": itinerary_id, "status": "placeholder", "message": "V1 API skeleton: persistent itinerary storage will be implemented in later steps."})
