from datetime import UTC, datetime
from uuid import UUID

from app.modules.organization.domain.entities import Department, Team
from app.modules.organization.domain.exceptions import (
    DepartmentInactiveError,
    DepartmentNameAlreadyExistsError,
    DepartmentNotFoundError,
    TeamNameAlreadyExistsError,
    TeamNotFoundError,
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

    def update_department(
        self,
        department_id: UUID,
        *,
        name: str | None,
        description: str | None,
        description_provided: bool,
    ) -> Department:
        department = self.get_department(department_id)
        changed_at = datetime.now(UTC)

        if name is not None:
            normalized_name = Department.normalize_name(name)
            existing_department = self._unit_of_work.departments.get_by_name(normalized_name)

            if existing_department is not None and existing_department.id != department.id:
                raise DepartmentNameAlreadyExistsError(normalized_name)

            department.rename(normalized_name, changed_at=changed_at)

        if description_provided:
            department.change_description(
                description,
                changed_at=changed_at,
            )

        try:
            updated_department = self._unit_of_work.departments.update(department)
            self._unit_of_work.commit()
        except Exception:
            self._unit_of_work.rollback()
            raise

        return updated_department

    def deactivate_department(self, department_id: UUID) -> None:
        department = self.get_department(department_id)

        if not department.is_active:
            return

        department.deactivate(changed_at=datetime.now(UTC))

        try:
            self._unit_of_work.departments.update(department)
            self._unit_of_work.commit()
        except Exception:
            self._unit_of_work.rollback()
            raise


class TeamService:
    def __init__(self, unit_of_work: OrganizationUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def create_team(
        self,
        department_id: UUID,
        *,
        name: str,
        description: str | None,
    ) -> Team:
        department = self._unit_of_work.departments.get_by_id(department_id)

        if department is None:
            raise DepartmentNotFoundError(department_id)

        if not department.is_active:
            raise DepartmentInactiveError(department_id)

        normalized_name = Team.normalize_name(name)
        normalized_description = Team.normalize_description(description)

        existing_team = self._unit_of_work.teams.get_by_name(
            department_id=department_id,
            name=normalized_name,
        )

        if existing_team is not None:
            raise TeamNameAlreadyExistsError(
                normalized_name,
                department_id,
            )

        try:
            team = self._unit_of_work.teams.create(
                department_id=department_id,
                name=normalized_name,
                description=normalized_description,
            )
            self._unit_of_work.commit()
        except Exception:
            self._unit_of_work.rollback()
            raise

        return team

    def get_team(self, team_id: UUID) -> Team:
        team = self._unit_of_work.teams.get_by_id(team_id)

        if team is None:
            raise TeamNotFoundError(team_id)

        return team

    def list_teams(self, department_id: UUID) -> list[Team]:
        department = self._unit_of_work.departments.get_by_id(department_id)

        if department is None:
            raise DepartmentNotFoundError(department_id)

        return self._unit_of_work.teams.list_by_department(department_id)

    def update_team(
        self,
        team_id: UUID,
        *,
        name: str | None,
        description: str | None,
        description_provided: bool,
    ) -> Team:
        team = self.get_team(team_id)
        changed_at = datetime.now(UTC)

        if name is not None:
            normalized_name = Team.normalize_name(name)
            existing_team = self._unit_of_work.teams.get_by_name(
                department_id=team.department_id,
                name=normalized_name,
            )

            if existing_team is not None and existing_team.id != team.id:
                raise TeamNameAlreadyExistsError(
                    normalized_name,
                    team.department_id,
                )

            team.rename(normalized_name, changed_at=changed_at)

        if description_provided:
            team.change_description(
                description,
                changed_at=changed_at,
            )

        try:
            updated_team = self._unit_of_work.teams.update(team)
            self._unit_of_work.commit()
        except Exception:
            self._unit_of_work.rollback()
            raise

        return updated_team

    def deactivate_team(self, team_id: UUID) -> None:
        team = self.get_team(team_id)

        if not team.is_active:
            return

        team.deactivate(changed_at=datetime.now(UTC))

        try:
            self._unit_of_work.teams.update(team)
            self._unit_of_work.commit()
        except Exception:
            self._unit_of_work.rollback()
            raise
