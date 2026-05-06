from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.router import api_router
from backend.app.db.base import Base
from backend.app.db.session import engine
from backend.app import models  # noqa: F401
from backend.app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="TravelDu V1 Backend",
    description="旅渡 V1 后端 API：DeepSeek + 高德地图 + 本地 POI 知识库。",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health")
def health():
    return {"status": "ok", "service": "traveldu-backend"}
