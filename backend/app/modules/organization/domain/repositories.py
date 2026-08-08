from typing import Protocol
from uuid import UUID

from app.modules.organization.domain.entities import Department


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


class OrganizationUnitOfWork(Protocol):
    departments: DepartmentRepository

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
