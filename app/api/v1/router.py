from fastapi import APIRouter

from app.api.v1.endpoints import health, ingest, status

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(ingest.router, prefix="/nfe", tags=["nfe"])
api_router.include_router(status.router, prefix="/nfe", tags=["nfe"])
