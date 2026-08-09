from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.organization.domain.entities import Department, Team
from app.modules.organization.domain.exceptions import (
    DepartmentNotFoundError,
    TeamNotFoundError,
    EmployeeNotFoundError,
)
from app.modules.organization.infrastructure.models import (
    DepartmentModel,
    TeamModel,
    EmployeeModel,
    EmployeeWorkScheduleModel,
)
from app.modules.organization.domain.employee_entities import (
    Employee,
    Weekday,
    WeeklyWorkSchedule,
)


class SqlAlchemyDepartmentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        name: str,
        description: str | None,
    ) -> Department:
        timestamp = datetime.now(UTC)

        model = DepartmentModel(
            name=name,
            description=description,
            is_active=True,
            created_at=timestamp,
            updated_at=timestamp,
        )

        self._session.add(model)
        self._session.flush()
        self._session.refresh(model)

        return self._to_domain(model)

    def get_by_id(self, department_id: UUID) -> Department | None:
        model = self._session.get(DepartmentModel, department_id)

        if model is None:
            return None

        return self._to_domain(model)

    def get_by_name(self, name: str) -> Department | None:
        statement = select(DepartmentModel).where(
            func.lower(DepartmentModel.name) == name.strip().lower()
        )
        model = self._session.scalar(statement)

        if model is None:
            return None

        return self._to_domain(model)

    def list_all(self) -> list[Department]:
        statement = select(DepartmentModel).order_by(DepartmentModel.name)
        models = self._session.scalars(statement).all()

        return [self._to_domain(model) for model in models]

    def update(self, department: Department) -> Department:
        model = self._session.get(DepartmentModel, department.id)

        if model is None:
            raise DepartmentNotFoundError(department.id)

        model.name = department.name
        model.description = department.description
        model.is_active = department.is_active
        model.updated_at = department.updated_at

        self._session.flush()
        self._session.refresh(model)

        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: DepartmentModel) -> Department:
        return Department(
            id=model.id,
            name=model.name,
            description=model.description,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SqlAlchemyTeamRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        department_id: UUID,
        name: str,
        description: str | None,
    ) -> Team:
        timestamp = datetime.now(UTC)

        model = TeamModel(
            department_id=department_id,
            name=name,
            description=description,
            is_active=True,
            created_at=timestamp,
            updated_at=timestamp,
        )

        self._session.add(model)
        self._session.flush()
        self._session.refresh(model)

        return self._to_domain(model)

    def get_by_id(self, team_id: UUID) -> Team | None:
        model = self._session.get(TeamModel, team_id)

        if model is None:
            return None

        return self._to_domain(model)

    def get_by_name(
        self,
        *,
        department_id: UUID,
        name: str,
    ) -> Team | None:
        statement = select(TeamModel).where(
            TeamModel.department_id == department_id,
            func.lower(TeamModel.name) == name.strip().lower(),
        )
        model = self._session.scalar(statement)

        if model is None:
            return None

        return self._to_domain(model)

    def list_by_department(self, department_id: UUID) -> list[Team]:
        statement = (
            select(TeamModel)
            .where(TeamModel.department_id == department_id)
            .order_by(TeamModel.name)
        )
        models = self._session.scalars(statement).all()

        return [self._to_domain(model) for model in models]

    def update(self, team: Team) -> Team:
        model = self._session.get(TeamModel, team.id)

        if model is None:
            raise TeamNotFoundError(team.id)

        model.department_id = team.department_id
        model.name = team.name
        model.description = team.description
        model.is_active = team.is_active
        model.updated_at = team.updated_at

        self._session.flush()
        self._session.refresh(model)

        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: TeamModel) -> Team:
        return Team(
            id=model.id,
            department_id=model.department_id,
            name=model.name,
            description=model.description,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SqlAlchemyEmployeeRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        team_id: UUID,
        personnel_number: str | None,
        first_name: str,
        last_name: str,
        email: str,
        entry_date: date | None,
        exit_date: date | None,
        work_schedule: WeeklyWorkSchedule,
    ) -> Employee:
        timestamp = datetime.now(UTC)

        model = EmployeeModel(
            team_id=team_id,
            personnel_number=personnel_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            entry_date=entry_date,
            exit_date=exit_date,
            is_active=True,
            created_at=timestamp,
            updated_at=timestamp,
        )

        self._session.add(model)
        self._session.flush()

        self._add_work_schedule_rows(
            model.id,
            work_schedule,
        )

        self._session.refresh(model)
        return self._to_domain(model)

    def get_by_id(self, employee_id: UUID) -> Employee | None:
        model = self._session.get(EmployeeModel, employee_id)

        if model is None:
            return None

        return self._to_domain(model)

    def get_by_email(self, email: str) -> Employee | None:
        statement = select(EmployeeModel).where(
            func.lower(EmployeeModel.email) == email.strip().lower()
        )
        model = self._session.scalar(statement)

        if model is None:
            return None

        return self._to_domain(model)

    def get_by_personnel_number(
        self,
        personnel_number: str,
    ) -> Employee | None:
        statement = select(EmployeeModel).where(
            EmployeeModel.personnel_number == personnel_number.strip()
        )
        model = self._session.scalar(statement)

        if model is None:
            return None

        return self._to_domain(model)

    def list_by_team(self, team_id: UUID) -> list[Employee]:
        statement = (
            select(EmployeeModel)
            .where(EmployeeModel.team_id == team_id)
            .order_by(
                EmployeeModel.last_name,
                EmployeeModel.first_name,
            )
        )
        models = self._session.scalars(statement).all()

        return [self._to_domain(model) for model in models]

    def get_work_schedule(
        self,
        employee_id: UUID,
    ) -> WeeklyWorkSchedule:
        if self._session.get(EmployeeModel, employee_id) is None:
            raise EmployeeNotFoundError(employee_id)

        statement = select(EmployeeWorkScheduleModel).where(
            EmployeeWorkScheduleModel.employee_id == employee_id
        )
        rows = self._session.scalars(statement).all()

        return WeeklyWorkSchedule(
            hours_by_weekday={Weekday(row.weekday): row.planned_hours for row in rows}
        )

    def replace_work_schedule(
        self,
        employee_id: UUID,
        work_schedule: WeeklyWorkSchedule,
    ) -> None:
        if self._session.get(EmployeeModel, employee_id) is None:
            raise EmployeeNotFoundError(employee_id)

        statement = delete(EmployeeWorkScheduleModel).where(
            EmployeeWorkScheduleModel.employee_id == employee_id
        )
        self._session.execute(statement)
        self._add_work_schedule_rows(employee_id, work_schedule)

    def update(self, employee: Employee) -> Employee:
        model = self._session.get(EmployeeModel, employee.id)

        if model is None:
            raise EmployeeNotFoundError(employee.id)

        model.team_id = employee.team_id
        model.personnel_number = employee.personnel_number
        model.first_name = employee.first_name
        model.last_name = employee.last_name
        model.email = employee.email
        model.entry_date = employee.entry_date
        model.exit_date = employee.exit_date
        model.is_active = employee.is_active
        model.updated_at = employee.updated_at

        self._session.flush()
        self._session.refresh(model)

        return self._to_domain(model)

    def _add_work_schedule_rows(
        self,
        employee_id: UUID,
        work_schedule: WeeklyWorkSchedule,
    ) -> None:
        rows = [
            EmployeeWorkScheduleModel(
                employee_id=employee_id,
                weekday=int(weekday),
                planned_hours=hours,
            )
            for weekday, hours in work_schedule.hours_by_weekday.items()
            if hours > 0
        ]

        self._session.add_all(rows)
        self._session.flush()

    @staticmethod
    def _to_domain(model: EmployeeModel) -> Employee:
        return Employee(
            id=model.id,
            team_id=model.team_id,
            personnel_number=model.personnel_number,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            entry_date=model.entry_date,
            exit_date=model.exit_date,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
