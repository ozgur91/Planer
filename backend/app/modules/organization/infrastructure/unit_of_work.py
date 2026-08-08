from sqlalchemy.orm import Session

from app.modules.organization.domain.repositories import DepartmentRepository
from app.modules.organization.infrastructure.repositories import (
    SqlAlchemyDepartmentRepository,
)


class SqlAlchemyOrganizationUnitOfWork:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._departments = SqlAlchemyDepartmentRepository(session)

    @property
    def departments(self) -> DepartmentRepository:
        return self._departments

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
