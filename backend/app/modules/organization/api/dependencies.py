from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_database_session
from app.modules.organization.application.services import (
    DepartmentService,
    TeamService,
)
from app.modules.organization.infrastructure.unit_of_work import (
    SqlAlchemyOrganizationUnitOfWork,
)

DatabaseSession = Annotated[Session, Depends(get_database_session)]


def get_department_service(
    session: DatabaseSession,
) -> DepartmentService:
    unit_of_work = SqlAlchemyOrganizationUnitOfWork(session)
    return DepartmentService(unit_of_work)


def get_team_service(
    session: DatabaseSession,
) -> TeamService:
    unit_of_work = SqlAlchemyOrganizationUnitOfWork(session)
    return TeamService(unit_of_work)


DepartmentServiceDependency = Annotated[
    DepartmentService,
    Depends(get_department_service),
]

TeamServiceDependency = Annotated[
    TeamService,
    Depends(get_team_service),
]
