from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.session_state import UserSession
from backend.app.schemas.api_schema import SessionCreateRequest
from backend.app.schemas.common_schema import ok

router = APIRouter()


@router.post("")
def create_session(req: SessionCreateRequest, db: Session = Depends(get_db)):
    session_id = req.session_id or f"sess_{uuid.uuid4().hex}"
    session = db.execute(select(UserSession).where(UserSession.session_id == session_id)).scalar_one_or_none()
    now = datetime.utcnow().isoformat()
    if session is None:
        session = UserSession(session_id=session_id, status="active", last_active_at=now)
        db.add(session)
    else:
        session.status = "active"
        session.last_active_at = now
    db.commit()
    return ok({"session_id": session_id, "status": "active"})
