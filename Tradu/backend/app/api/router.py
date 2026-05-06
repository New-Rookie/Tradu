from fastapi import APIRouter

from backend.app.api import content_api, itinerary_api, llm_api, poi_api, route_api, service_poi_api, session_api, weather_api

api_router = APIRouter()
api_router.include_router(llm_api.router, prefix="/llm", tags=["LLM"])
api_router.include_router(content_api.router, prefix="/content", tags=["Content"])
api_router.include_router(poi_api.router, prefix="/pois", tags=["POI"])
api_router.include_router(route_api.router, prefix="/routes", tags=["Route"])
api_router.include_router(weather_api.router, prefix="/weather", tags=["Weather"])
api_router.include_router(itinerary_api.router, prefix="/itineraries", tags=["Itinerary"])
api_router.include_router(session_api.router, prefix="/sessions", tags=["Sessions"])
api_router.include_router(service_poi_api.router, prefix="/service-pois", tags=["Service POI"])
