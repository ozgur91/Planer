from fastapi import APIRouter

from app.api.health import router as health_router
from app.modules.organization.api.router import router as organization_router
from app.modules.organization.api.team_router import router as team_router

from app.modules.organization.api.employee_router import (
    router as employee_router,
)

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(organization_router)
api_router.include_router(team_router)
api_router.include_router(employee_router)
