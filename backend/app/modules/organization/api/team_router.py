from uuid import UUID

from fastapi import APIRouter, Response, status

from app.modules.organization.api.dependencies import TeamServiceDependency
from app.modules.organization.api.schemas import (
    TeamCreateRequest,
    TeamResponse,
    TeamUpdateRequest,
)

router = APIRouter(tags=["Teams"])


@router.post(
    "/departments/{department_id}/teams",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_team(
    department_id: UUID,
    request: TeamCreateRequest,
    service: TeamServiceDependency,
) -> TeamResponse:
    team = service.create_team(
        department_id,
        name=request.name,
        description=request.description,
    )
    return TeamResponse.model_validate(team)


@router.get(
    "/departments/{department_id}/teams",
    response_model=list[TeamResponse],
)
def list_teams(
    department_id: UUID,
    service: TeamServiceDependency,
) -> list[TeamResponse]:
    teams = service.list_teams(department_id)

    return [TeamResponse.model_validate(team) for team in teams]


@router.get(
    "/teams/{team_id}",
    response_model=TeamResponse,
)
def get_team(
    team_id: UUID,
    service: TeamServiceDependency,
) -> TeamResponse:
    team = service.get_team(team_id)
    return TeamResponse.model_validate(team)


@router.patch(
    "/teams/{team_id}",
    response_model=TeamResponse,
)
def update_team(
    team_id: UUID,
    request: TeamUpdateRequest,
    service: TeamServiceDependency,
) -> TeamResponse:
    team = service.update_team(
        team_id,
        name=request.name,
        description=request.description,
        description_provided="description" in request.model_fields_set,
    )
    return TeamResponse.model_validate(team)


@router.delete(
    "/teams/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deactivate_team(
    team_id: UUID,
    service: TeamServiceDependency,
) -> Response:
    service.deactivate_team(team_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
