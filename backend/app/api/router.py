from fastapi import APIRouter

from app.api.health import router as health_router
from app.modules.organization.api.router import router as organization_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(organization_router)
