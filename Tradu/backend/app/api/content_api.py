from fastapi import APIRouter, HTTPException

from backend.app.schemas.api_schema import NoteExtractRequest
from backend.app.schemas.common_schema import ok
from backend.app.services.deepseek_api_service import DeepSeekApiService

router = APIRouter()


@router.post("/extract")
def extract_note(req: NoteExtractRequest):
    try:
        data = DeepSeekApiService().extract_note(req.text)
        return ok(data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
