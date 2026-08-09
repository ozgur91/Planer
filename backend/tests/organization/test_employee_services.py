from collections.abc import Generator
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.modules.organization.application.services import (
    DepartmentService,
    EmployeeService,
    TeamService,
)
from app.modules.organization.domain.employee_entities import (
    Weekday,
    WeeklyWorkSchedule,
)
from app.modules.organization.domain.exceptions import (
    EmployeeEmailAlreadyExistsError,
    EmployeePersonnelNumberAlreadyExistsError,
    TeamInactiveError,
    TeamNotFoundError,
)
from app.modules.organization.infrastructure.unit_of_work import (
    SqlAlchemyOrganizationUnitOfWork,
)


@pytest.fixture
def services() -> Generator[tuple[DepartmentService, TeamService, EmployeeService]]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        unit_of_work = SqlAlchemyOrganizationUnitOfWork(session)
        yield (
            DepartmentService(unit_of_work),
            TeamService(unit_of_work),
            EmployeeService(unit_of_work),
        )

    Base.metadata.drop_all(engine)
    engine.dispose()


def create_team(
    department_service: DepartmentService,
    team_service: TeamService,
):
    department = department_service.create_department(
        name="Entwicklung",
        description=None,
    )
    return team_service.create_team(
        department.id,
        name="Backend",
        description=None,
    )


def create_schedule() -> WeeklyWorkSchedule:
    return WeeklyWorkSchedule(
        hours_by_weekday={
            Weekday.MONDAY: Decimal("7.7"),
            Weekday.TUESDAY: Decimal("7.7"),
            Weekday.WEDNESDAY: Decimal("3.85"),
        }
    )


def test_service_creates_employee_with_schedule(
    services: tuple[DepartmentService, TeamService, EmployeeService],
) -> None:
    department_service, team_service, employee_service = services
    team = create_team(department_service, team_service)

    employee = employee_service.create_employee(
        team_id=team.id,
        personnel_number="  10042  ",
        first_name="  Erika  ",
        last_name="  Mustermann  ",
        email="  Erika.Mustermann@EXAMPLE.COM  ",
        entry_date=None,
        exit_date=None,
        work_schedule=create_schedule(),
    )
    schedule = employee_service.get_work_schedule(employee.id)

    assert employee.personnel_number == "10042"
    assert employee.first_name == "Erika"
    assert employee.email == "erika.mustermann@example.com"
    assert schedule.total_weekly_hours() == Decimal("19.25")


def test_service_rejects_unknown_team(
    services: tuple[DepartmentService, TeamService, EmployeeService],
) -> None:
    _, _, employee_service = services

    with pytest.raises(TeamNotFoundError):
        employee_service.create_employee(
            team_id=uuid4(),
            personnel_number=None,
            first_name="Erika",
            last_name="Mustermann",
            email="erika@example.com",
            entry_date=None,
            exit_date=None,
            work_schedule=create_schedule(),
        )


def test_service_rejects_inactive_team(
    services: tuple[DepartmentService, TeamService, EmployeeService],
) -> None:
    department_service, team_service, employee_service = services
    team = create_team(department_service, team_service)
    team_service.deactivate_team(team.id)

    with pytest.raises(TeamInactiveError):
        employee_service.create_employee(
            team_id=team.id,
            personnel_number=None,
            first_name="Erika",
            last_name="Mustermann",
            email="erika@example.com",
            entry_date=None,
            exit_date=None,
            work_schedule=create_schedule(),
        )


def test_service_rejects_duplicate_email_and_personnel_number(
    services: tuple[DepartmentService, TeamService, EmployeeService],
) -> None:
    department_service, team_service, employee_service = services
    team = create_team(department_service, team_service)

    employee_service.create_employee(
        team_id=team.id,
        personnel_number="10042",
        first_name="Erika",
        last_name="Mustermann",
        email="erika@example.com",
        entry_date=None,
        exit_date=None,
        work_schedule=create_schedule(),
    )

    with pytest.raises(EmployeeEmailAlreadyExistsError):
        employee_service.create_employee(
            team_id=team.id,
            personnel_number="10043",
            first_name="Andere",
            last_name="Person",
            email="ERIKA@EXAMPLE.COM",
            entry_date=None,
            exit_date=None,
            work_schedule=create_schedule(),
        )

    with pytest.raises(EmployeePersonnelNumberAlreadyExistsError):
        employee_service.create_employee(
            team_id=team.id,
            personnel_number="10042",
            first_name="Andere",
            last_name="Person",
            email="andere@example.com",
            entry_date=None,
            exit_date=None,
            work_schedule=create_schedule(),
        )
