from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from app.modules.organization.application.services import DepartmentService
from app.modules.organization.domain.entities import Department
from app.modules.organization.domain.exceptions import (
    DepartmentNameAlreadyExistsError,
    DepartmentNotFoundError,
)


class FakeDepartmentRepository:
    def __init__(self) -> None:
        self.departments: dict[UUID, Department] = {}

    def create(
        self,
        *,
        name: str,
        description: str | None,
    ) -> Department:
        timestamp = datetime.now(UTC)
        department = Department(
            id=uuid4(),
            name=name,
            description=description,
            is_active=True,
            created_at=timestamp,
            updated_at=timestamp,
        )
        self.departments[department.id] = department
        return department

    def get_by_id(self, department_id: UUID) -> Department | None:
        return self.departments.get(department_id)

    def get_by_name(self, name: str) -> Department | None:
        normalized_name = name.casefold()

        return next(
            (
                department
                for department in self.departments.values()
                if department.name.casefold() == normalized_name
            ),
            None,
        )

    def list_all(self) -> list[Department]:
        return sorted(
            self.departments.values(),
            key=lambda department: department.name,
        )

    def update(self, department: Department) -> Department:
        self.departments[department.id] = department
        return department


class FakeTeamRepository:
    pass


class FakeOrganizationUnitOfWork:
    def __init__(self) -> None:
        self.departments = FakeDepartmentRepository()
        self.teams = FakeTeamRepository()
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


def test_service_creates_normalized_department() -> None:
    unit_of_work = FakeOrganizationUnitOfWork()
    service = DepartmentService(unit_of_work)

    department = service.create_department(
        name="  Softwareentwicklung  ",
        description="  Interne Anwendungen  ",
    )

    assert department.name == "Softwareentwicklung"
    assert department.description == "Interne Anwendungen"
    assert unit_of_work.committed is True
    assert unit_of_work.rolled_back is False


def test_service_rejects_duplicate_department_name() -> None:
    unit_of_work = FakeOrganizationUnitOfWork()
    service = DepartmentService(unit_of_work)

    service.create_department(
        name="Softwareentwicklung",
        description=None,
    )

    with pytest.raises(DepartmentNameAlreadyExistsError):
        service.create_department(
            name="SOFTWAREENTWICKLUNG",
            description=None,
        )


def test_service_raises_error_for_unknown_department() -> None:
    service = DepartmentService(FakeOrganizationUnitOfWork())

    with pytest.raises(DepartmentNotFoundError):
        service.get_department(uuid4())
