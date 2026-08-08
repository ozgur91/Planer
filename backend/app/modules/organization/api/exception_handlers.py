from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.modules.organization.domain.exceptions import (
    DepartmentInactiveError,
    DepartmentNameAlreadyExistsError,
    DepartmentNotFoundError,
    InvalidDepartmentNameError,
    InvalidTeamNameError,
    TeamNameAlreadyExistsError,
    TeamNotFoundError,
)


def register_organization_exception_handlers(application: FastAPI) -> None:
    @application.exception_handler(DepartmentNotFoundError)
    async def handle_department_not_found(
        _request: Request,
        exception: DepartmentNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exception)},
        )

    @application.exception_handler(DepartmentNameAlreadyExistsError)
    async def handle_duplicate_department_name(
        _request: Request,
        exception: DepartmentNameAlreadyExistsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exception)},
        )

    @application.exception_handler(InvalidDepartmentNameError)
    async def handle_invalid_department_name(
        _request: Request,
        exception: InvalidDepartmentNameError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": str(exception)},
        )

    @application.exception_handler(DepartmentInactiveError)
    async def handle_inactive_department(
        _request: Request,
        exception: DepartmentInactiveError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exception)},
        )

    @application.exception_handler(TeamNotFoundError)
    async def handle_team_not_found(
        _request: Request,
        exception: TeamNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exception)},
        )

    @application.exception_handler(TeamNameAlreadyExistsError)
    async def handle_duplicate_team_name(
        _request: Request,
        exception: TeamNameAlreadyExistsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exception)},
        )

    @application.exception_handler(InvalidTeamNameError)
    async def handle_invalid_team_name(
        _request: Request,
        exception: InvalidTeamNameError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": str(exception)},
        )
