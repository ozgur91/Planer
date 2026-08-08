from typing import Protocol
from uuid import UUID

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


class OrganizationUnitOfWork(Protocol):
    departments: DepartmentRepository
    teams: TeamRepository

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
