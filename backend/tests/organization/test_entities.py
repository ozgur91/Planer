from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.modules.organization.domain.entities import Department
from app.modules.organization.domain.exceptions import InvalidDepartmentNameError


def create_department() -> Department:
    timestamp = datetime(2026, 8, 8, tzinfo=UTC)

    return Department(
        id=uuid4(),
        name="Softwareentwicklung",
        description="Interne Software",
        is_active=True,
        created_at=timestamp,
        updated_at=timestamp,
    )


def test_department_normalizes_name_and_description() -> None:
    timestamp = datetime(2026, 8, 8, tzinfo=UTC)

    department = Department(
        id=uuid4(),
        name="  Softwareentwicklung  ",
        description="  Interne Software  ",
        is_active=True,
        created_at=timestamp,
        updated_at=timestamp,
    )

    assert department.name == "Softwareentwicklung"
    assert department.description == "Interne Software"


def test_department_rejects_empty_name() -> None:
    timestamp = datetime(2026, 8, 8, tzinfo=UTC)

    with pytest.raises(
        InvalidDepartmentNameError,
        match="name must not be empty",
    ):
        Department(
            id=uuid4(),
            name="   ",
            description=None,
            is_active=True,
            created_at=timestamp,
            updated_at=timestamp,
        )


def test_department_rename_updates_name_and_timestamp() -> None:
    department = create_department()
    changed_at = datetime(2026, 8, 9, tzinfo=UTC)

    department.rename(
        "  IT-Entwicklung  ",
        changed_at=changed_at,
    )

    assert department.name == "IT-Entwicklung"
    assert department.updated_at == changed_at


def test_department_can_be_deactivated() -> None:
    department = create_department()
    changed_at = datetime(2026, 8, 9, tzinfo=UTC)

    department.deactivate(changed_at=changed_at)

    assert department.is_active is False
    assert department.updated_at == changed_at
