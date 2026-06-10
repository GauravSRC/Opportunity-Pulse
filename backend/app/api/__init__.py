"""API routers aggregator."""

from fastapi import APIRouter

from app.api import (
    admin,
    alerts,
    deadlines,
    feedback,
    opportunities,
    outreach,
    profiles,
    sources,
)

api_router = APIRouter()
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
api_router.include_router(outreach.router, tags=["outreach"])
api_router.include_router(deadlines.router, prefix="/deadlines", tags=["deadlines"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
