from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.modules.organization.domain.entities import Team
from app.modules.organization.domain.exceptions import InvalidTeamNameError


def test_team_normalizes_name_and_description() -> None:
    timestamp = datetime(2026, 8, 9, tzinfo=UTC)

    team = Team(
        id=uuid4(),
        department_id=uuid4(),
        name="  Backend  ",
        description="  Backend-Entwicklung  ",
        is_active=True,
        created_at=timestamp,
        updated_at=timestamp,
    )

    assert team.name == "Backend"
    assert team.description == "Backend-Entwicklung"


def test_team_rejects_empty_name() -> None:
    timestamp = datetime(2026, 8, 9, tzinfo=UTC)

    with pytest.raises(InvalidTeamNameError, match="must not be empty"):
        Team(
            id=uuid4(),
            department_id=uuid4(),
            name="   ",
            description=None,
            is_active=True,
            created_at=timestamp,
            updated_at=timestamp,
        )


def test_team_can_be_deactivated() -> None:
    timestamp = datetime(2026, 8, 9, tzinfo=UTC)
    changed_at = datetime(2026, 8, 10, tzinfo=UTC)
    team = Team(
        id=uuid4(),
        department_id=uuid4(),
        name="Backend",
        description=None,
        is_active=True,
        created_at=timestamp,
        updated_at=timestamp,
    )

    team.deactivate(changed_at=changed_at)

    assert team.is_active is False
    assert team.updated_at == changed_at
