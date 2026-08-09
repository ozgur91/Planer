from collections.abc import Generator
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.modules.organization.domain.employee_entities import (
    Weekday,
    WeeklyWorkSchedule,
)
from app.modules.organization.infrastructure.repositories import (
    SqlAlchemyDepartmentRepository,
    SqlAlchemyEmployeeRepository,
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


def create_team(database_session: Session):
    department_repository = SqlAlchemyDepartmentRepository(database_session)
    team_repository = SqlAlchemyTeamRepository(database_session)

    department = department_repository.create(
        name="Entwicklung",
        description=None,
    )
    return team_repository.create(
        department_id=department.id,
        name="Backend",
        description=None,
    )


def test_repository_creates_employee_with_work_schedule(
    database_session: Session,
) -> None:
    team = create_team(database_session)
    repository = SqlAlchemyEmployeeRepository(database_session)
    schedule = WeeklyWorkSchedule(
        hours_by_weekday={
            Weekday.MONDAY: Decimal("7.7"),
            Weekday.TUESDAY: Decimal("3.85"),
        }
    )

    employee = repository.create(
        team_id=team.id,
        personnel_number="10042",
        first_name="Erika",
        last_name="Mustermann",
        email="erika.mustermann@example.com",
        entry_date=None,
        exit_date=None,
        work_schedule=schedule,
    )
    loaded_schedule = repository.get_work_schedule(employee.id)

    assert employee.team_id == team.id
    assert employee.email == "erika.mustermann@example.com"
    assert loaded_schedule.hours_for_weekday(Weekday.MONDAY) == Decimal("7.70")
    assert loaded_schedule.hours_for_weekday(Weekday.TUESDAY) == Decimal("3.85")
    assert loaded_schedule.hours_for_weekday(Weekday.FRIDAY) == Decimal("0")


def test_repository_replaces_work_schedule(
    database_session: Session,
) -> None:
    team = create_team(database_session)
    repository = SqlAlchemyEmployeeRepository(database_session)

    employee = repository.create(
        team_id=team.id,
        personnel_number=None,
        first_name="Max",
        last_name="Mustermann",
        email="max.mustermann@example.com",
        entry_date=None,
        exit_date=None,
        work_schedule=WeeklyWorkSchedule(
            hours_by_weekday={
                Weekday.MONDAY: Decimal("7.7"),
            }
        ),
    )

    repository.replace_work_schedule(
        employee.id,
        WeeklyWorkSchedule(
            hours_by_weekday={
                Weekday.WEDNESDAY: Decimal("3.85"),
            }
        ),
    )
    loaded_schedule = repository.get_work_schedule(employee.id)

    assert loaded_schedule.hours_for_weekday(Weekday.MONDAY) == Decimal("0")
    assert loaded_schedule.hours_for_weekday(Weekday.WEDNESDAY) == Decimal("3.85")
