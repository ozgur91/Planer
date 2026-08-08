from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.modules.organization.api.exception_handlers import (
    register_organization_exception_handlers,
)


def create_app() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        description="Backend API for the Planer application",
        version=settings.app_version,
    )
    application.include_router(
        api_router,
        prefix=settings.api_v1_prefix,
    )
    register_organization_exception_handlers(application)

    return application


app = create_app()
