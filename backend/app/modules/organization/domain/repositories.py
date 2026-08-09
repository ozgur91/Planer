from datetime import date
from typing import Protocol
from uuid import UUID

from app.modules.organization.domain.employee_entities import (
    Employee,
    WeeklyWorkSchedule,
)
from app.modules.organization.domain.entities import Department, Team


class DepartmentRepository(Protocol):
    def create(
        self,
        *,
        name: str,
        description: str | None,
    ) -> Department: ...

    def get_by_id(self, department_id: UUID) -> Department | None: ...

    def get_by_name(self, name: str) -> Department | None: ...

    def list_all(self) -> list[Department]: ...

    def update(self, department: Department) -> Department: ...


class TeamRepository(Protocol):
    def create(
        self,
        *,
        department_id: UUID,
        name: str,
        description: str | None,
    ) -> Team: ...

    def get_by_id(self, team_id: UUID) -> Team | None: ...

    def get_by_name(
        self,
        *,
        department_id: UUID,
        name: str,
    ) -> Team | None: ...

    def list_by_department(self, department_id: UUID) -> list[Team]: ...

    def update(self, team: Team) -> Team: ...


class EmployeeRepository(Protocol):
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
    ) -> Employee: ...

    def get_by_id(self, employee_id: UUID) -> Employee | None: ...

    def get_by_email(self, email: str) -> Employee | None: ...

    def get_by_personnel_number(
        self,
        personnel_number: str,
    ) -> Employee | None: ...

    def list_by_team(self, team_id: UUID) -> list[Employee]: ...

    def get_work_schedule(
        self,
        employee_id: UUID,
    ) -> WeeklyWorkSchedule: ...

    def replace_work_schedule(
        self,
        employee_id: UUID,
        work_schedule: WeeklyWorkSchedule,
    ) -> None: ...

    def update(self, employee: Employee) -> Employee: ...


class OrganizationUnitOfWork(Protocol):
    departments: DepartmentRepository
    teams: TeamRepository
    employees: EmployeeRepository

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
