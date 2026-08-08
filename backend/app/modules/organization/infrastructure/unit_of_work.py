from sqlalchemy.orm import Session

from app.modules.organization.domain.repositories import (
    DepartmentRepository,
    TeamRepository,
)
from app.modules.organization.infrastructure.repositories import (
    SqlAlchemyDepartmentRepository,
    SqlAlchemyTeamRepository,
)


class SqlAlchemyOrganizationUnitOfWork:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._departments = SqlAlchemyDepartmentRepository(session)
        self._teams = SqlAlchemyTeamRepository(session)

    @property
    def departments(self) -> DepartmentRepository:
        return self._departments

    @property
    def teams(self) -> TeamRepository:
        return self._teams

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
