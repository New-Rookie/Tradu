from fastapi import APIRouter, HTTPException

from backend.app.schemas.api_schema import TextRequest, IntentParseRequest
from backend.app.schemas.common_schema import ok
from backend.app.services.deepseek_api_service import DeepSeekApiService

router = APIRouter()


@router.post("/parse-intent")
def parse_intent(req: IntentParseRequest):
    try:
        data = DeepSeekApiService().parse_intent(req.text)
        return ok(data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/parse-adjustment")
def parse_adjustment(req: TextRequest):
    try:
        data = DeepSeekApiService().parse_adjustment(req.text)
        return ok(data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
