from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.modules.organization.infrastructure.repositories import (
    SqlAlchemyDepartmentRepository,
)


@pytest.fixture
def database_session() -> Generator[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(engine)
    engine.dispose()


def test_repository_creates_and_reads_department(
    database_session: Session,
) -> None:
    repository = SqlAlchemyDepartmentRepository(database_session)

    created_department = repository.create(
        name="Softwareentwicklung",
        description="Entwicklung interner Anwendungen",
    )

    loaded_department = repository.get_by_id(created_department.id)

    assert loaded_department is not None
    assert loaded_department.id == created_department.id
    assert loaded_department.name == "Softwareentwicklung"
    assert loaded_department.description == "Entwicklung interner Anwendungen"
    assert loaded_department.is_active is True


def test_repository_finds_department_case_insensitively(
    database_session: Session,
) -> None:
    repository = SqlAlchemyDepartmentRepository(database_session)
    repository.create(
        name="Softwareentwicklung",
        description=None,
    )

    department = repository.get_by_name("softwareENTWICKLUNG")

    assert department is not None
    assert department.name == "Softwareentwicklung"


def test_repository_lists_departments_ordered_by_name(
    database_session: Session,
) -> None:
    repository = SqlAlchemyDepartmentRepository(database_session)
    repository.create(name="Vertrieb", description=None)
    repository.create(name="Entwicklung", description=None)

    departments = repository.list_all()

    assert [department.name for department in departments] == [
        "Entwicklung",
        "Vertrieb",
    ]
