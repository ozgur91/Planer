from collections.abc import Generator
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.modules.organization.application.services import (
    DepartmentService,
    TeamService,
)
from app.modules.organization.domain.exceptions import (
    DepartmentInactiveError,
    DepartmentNotFoundError,
    TeamNameAlreadyExistsError,
)
from app.modules.organization.infrastructure.unit_of_work import (
    SqlAlchemyOrganizationUnitOfWork,
)


@pytest.fixture
def services() -> Generator[tuple[DepartmentService, TeamService]]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        unit_of_work = SqlAlchemyOrganizationUnitOfWork(session)
        yield (
            DepartmentService(unit_of_work),
            TeamService(unit_of_work),
        )

    Base.metadata.drop_all(engine)
    engine.dispose()


def test_service_creates_team_in_department(
    services: tuple[DepartmentService, TeamService],
) -> None:
    department_service, team_service = services
    department = department_service.create_department(
        name="Softwareentwicklung",
        description=None,
    )

    team = team_service.create_team(
        department.id,
        name="  Backend  ",
        description="  Backend-Entwicklung  ",
    )

    assert team.department_id == department.id
    assert team.name == "Backend"
    assert team.description == "Backend-Entwicklung"
    assert team.is_active is True


def test_service_rejects_unknown_department(
    services: tuple[DepartmentService, TeamService],
) -> None:
    _, team_service = services

    with pytest.raises(DepartmentNotFoundError):
        team_service.create_team(
            uuid4(),
            name="Backend",
            description=None,
        )


def test_service_rejects_inactive_department(
    services: tuple[DepartmentService, TeamService],
) -> None:
    department_service, team_service = services
    department = department_service.create_department(
        name="Softwareentwicklung",
        description=None,
    )
    department_service.deactivate_department(department.id)

    with pytest.raises(DepartmentInactiveError):
        team_service.create_team(
            department.id,
            name="Backend",
            description=None,
        )


def test_service_rejects_duplicate_team_name_in_department(
    services: tuple[DepartmentService, TeamService],
) -> None:
    department_service, team_service = services
    department = department_service.create_department(
        name="Softwareentwicklung",
        description=None,
    )
    team_service.create_team(
        department.id,
        name="Backend",
        description=None,
    )

    with pytest.raises(TeamNameAlreadyExistsError):
        team_service.create_team(
            department.id,
            name="BACKEND",
            description=None,
        )
