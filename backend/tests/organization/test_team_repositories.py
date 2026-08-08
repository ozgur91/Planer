from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.modules.organization.infrastructure.repositories import (
    SqlAlchemyDepartmentRepository,
    SqlAlchemyTeamRepository,
)


@pytest.fixture
def database_session() -> Generator[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(engine)
    engine.dispose()


def test_repository_creates_and_reads_team(
    database_session: Session,
) -> None:
    department_repository = SqlAlchemyDepartmentRepository(database_session)
    team_repository = SqlAlchemyTeamRepository(database_session)

    department = department_repository.create(
        name="Softwareentwicklung",
        description=None,
    )
    created_team = team_repository.create(
        department_id=department.id,
        name="Backend",
        description="Backend-Entwicklung",
    )

    loaded_team = team_repository.get_by_id(created_team.id)

    assert loaded_team is not None
    assert loaded_team.id == created_team.id
    assert loaded_team.department_id == department.id
    assert loaded_team.name == "Backend"
    assert loaded_team.description == "Backend-Entwicklung"


def test_repository_finds_team_name_within_department(
    database_session: Session,
) -> None:
    department_repository = SqlAlchemyDepartmentRepository(database_session)
    team_repository = SqlAlchemyTeamRepository(database_session)

    department = department_repository.create(
        name="Softwareentwicklung",
        description=None,
    )
    team_repository.create(
        department_id=department.id,
        name="Backend",
        description=None,
    )

    team = team_repository.get_by_name(
        department_id=department.id,
        name="BACKEND",
    )

    assert team is not None
    assert team.name == "Backend"


def test_repository_lists_only_teams_from_requested_department(
    database_session: Session,
) -> None:
    department_repository = SqlAlchemyDepartmentRepository(database_session)
    team_repository = SqlAlchemyTeamRepository(database_session)

    development = department_repository.create(
        name="Entwicklung",
        description=None,
    )
    sales = department_repository.create(
        name="Vertrieb",
        description=None,
    )

    team_repository.create(
        department_id=development.id,
        name="Frontend",
        description=None,
    )
    team_repository.create(
        department_id=development.id,
        name="Backend",
        description=None,
    )
    team_repository.create(
        department_id=sales.id,
        name="Innendienst",
        description=None,
    )

    teams = team_repository.list_by_department(development.id)

    assert [team.name for team in teams] == ["Backend", "Frontend"]
