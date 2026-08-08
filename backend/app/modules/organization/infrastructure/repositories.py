from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.organization.domain.entities import Department, Team
from app.modules.organization.domain.exceptions import (
    DepartmentNotFoundError,
    TeamNotFoundError,
)
from app.modules.organization.infrastructure.models import (
    DepartmentModel,
    TeamModel,
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
