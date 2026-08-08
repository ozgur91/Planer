from uuid import UUID

from app.modules.organization.domain.entities import Department
from app.modules.organization.domain.exceptions import (
    DepartmentNameAlreadyExistsError,
    DepartmentNotFoundError,
)
from app.modules.organization.domain.repositories import OrganizationUnitOfWork


class DepartmentService:
    def __init__(self, unit_of_work: OrganizationUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def create_department(
        self,
        *,
        name: str,
        description: str | None,
    ) -> Department:
        normalized_name = Department.normalize_name(name)
        normalized_description = Department.normalize_description(description)

        existing_department = self._unit_of_work.departments.get_by_name(normalized_name)

        if existing_department is not None:
            raise DepartmentNameAlreadyExistsError(normalized_name)

        try:
            department = self._unit_of_work.departments.create(
                name=normalized_name,
                description=normalized_description,
            )
            self._unit_of_work.commit()
        except Exception:
            self._unit_of_work.rollback()
            raise

        return department

    def get_department(self, department_id: UUID) -> Department:
        department = self._unit_of_work.departments.get_by_id(department_id)

        if department is None:
            raise DepartmentNotFoundError(department_id)

        return department

    def list_departments(self) -> list[Department]:
        return self._unit_of_work.departments.list_all()
