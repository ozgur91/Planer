from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_database_session
from app.main import create_app


@pytest.fixture
def client() -> Generator[TestClient]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(engine)

    def override_database_session() -> Generator[Session]:
        with testing_session_factory() as session:
            yield session

    application = create_app()
    application.dependency_overrides[get_database_session] = override_database_session

    with TestClient(application) as test_client:
        yield test_client

    application.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_create_department_returns_created_department(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/departments",
        json={
            "name": "Softwareentwicklung",
            "description": "Entwicklung interner Software",
        },
    )

    assert response.status_code == 201

    response_body = response.json()
    assert response_body["name"] == "Softwareentwicklung"
    assert response_body["description"] == "Entwicklung interner Software"
    assert response_body["is_active"] is True
    assert response_body["id"]


def test_list_departments_returns_created_departments(
    client: TestClient,
) -> None:
    client.post(
        "/api/v1/departments",
        json={"name": "Vertrieb", "description": None},
    )
    client.post(
        "/api/v1/departments",
        json={"name": "Entwicklung", "description": None},
    )

    response = client.get("/api/v1/departments")

    assert response.status_code == 200
    assert [department["name"] for department in response.json()] == [
        "Entwicklung",
        "Vertrieb",
    ]


def test_get_department_returns_department(
    client: TestClient,
) -> None:
    create_response = client.post(
        "/api/v1/departments",
        json={
            "name": "Softwareentwicklung",
            "description": None,
        },
    )
    department_id = create_response.json()["id"]

    response = client.get(f"/api/v1/departments/{department_id}")

    assert response.status_code == 200
    assert response.json()["id"] == department_id
    assert response.json()["name"] == "Softwareentwicklung"


def test_get_unknown_department_returns_not_found(
    client: TestClient,
) -> None:
    response = client.get(f"/api/v1/departments/{uuid4()}")

    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]


def test_duplicate_department_name_returns_conflict(
    client: TestClient,
) -> None:
    first_response = client.post(
        "/api/v1/departments",
        json={"name": "Softwareentwicklung", "description": None},
    )
    second_response = client.post(
        "/api/v1/departments",
        json={"name": "SOFTWAREENTWICKLUNG", "description": None},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert "already exists" in second_response.json()["detail"]


def test_whitespace_only_department_name_is_rejected(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/departments",
        json={"name": "   ", "description": None},
    )

    assert response.status_code == 422
    assert "name must not be empty" in response.json()["detail"]


def test_update_department_changes_name_and_description(
    client: TestClient,
) -> None:
    create_response = client.post(
        "/api/v1/departments",
        json={
            "name": "Entwicklung",
            "description": "Alte Beschreibung",
        },
    )
    department_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/departments/{department_id}",
        json={
            "name": "Softwareentwicklung",
            "description": "Neue Beschreibung",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Softwareentwicklung"
    assert response.json()["description"] == "Neue Beschreibung"


def test_update_department_can_remove_description(
    client: TestClient,
) -> None:
    create_response = client.post(
        "/api/v1/departments",
        json={
            "name": "Entwicklung",
            "description": "Beschreibung",
        },
    )
    department_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/departments/{department_id}",
        json={"description": None},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Entwicklung"
    assert response.json()["description"] is None


def test_update_department_rejects_duplicate_name(
    client: TestClient,
) -> None:
    client.post(
        "/api/v1/departments",
        json={"name": "Entwicklung", "description": None},
    )
    create_response = client.post(
        "/api/v1/departments",
        json={"name": "Vertrieb", "description": None},
    )
    department_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/departments/{department_id}",
        json={"name": "ENTWICKLUNG"},
    )

    assert response.status_code == 409


def test_delete_department_deactivates_department(
    client: TestClient,
) -> None:
    create_response = client.post(
        "/api/v1/departments",
        json={"name": "Entwicklung", "description": None},
    )
    department_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/departments/{department_id}")
    get_response = client.get(f"/api/v1/departments/{department_id}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_create_team_in_department(client: TestClient) -> None:
    department_response = client.post(
        "/api/v1/departments",
        json={"name": "Entwicklung", "description": None},
    )
    department_id = department_response.json()["id"]

    response = client.post(
        f"/api/v1/departments/{department_id}/teams",
        json={
            "name": "Backend",
            "description": "Backend-Entwicklung",
        },
    )

    assert response.status_code == 201
    assert response.json()["department_id"] == department_id
    assert response.json()["name"] == "Backend"
    assert response.json()["is_active"] is True


def test_list_teams_from_department(client: TestClient) -> None:
    department_response = client.post(
        "/api/v1/departments",
        json={"name": "Entwicklung", "description": None},
    )
    department_id = department_response.json()["id"]

    client.post(
        f"/api/v1/departments/{department_id}/teams",
        json={"name": "Frontend", "description": None},
    )
    client.post(
        f"/api/v1/departments/{department_id}/teams",
        json={"name": "Backend", "description": None},
    )

    response = client.get(f"/api/v1/departments/{department_id}/teams")

    assert response.status_code == 200
    assert [team["name"] for team in response.json()] == [
        "Backend",
        "Frontend",
    ]


def test_create_team_rejects_unknown_department(
    client: TestClient,
) -> None:
    response = client.post(
        f"/api/v1/departments/{uuid4()}/teams",
        json={"name": "Backend", "description": None},
    )

    assert response.status_code == 404


def test_create_team_rejects_duplicate_name(
    client: TestClient,
) -> None:
    department_response = client.post(
        "/api/v1/departments",
        json={"name": "Entwicklung", "description": None},
    )
    department_id = department_response.json()["id"]

    first_response = client.post(
        f"/api/v1/departments/{department_id}/teams",
        json={"name": "Backend", "description": None},
    )
    second_response = client.post(
        f"/api/v1/departments/{department_id}/teams",
        json={"name": "BACKEND", "description": None},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_update_and_deactivate_team(client: TestClient) -> None:
    department_response = client.post(
        "/api/v1/departments",
        json={"name": "Entwicklung", "description": None},
    )
    department_id = department_response.json()["id"]

    create_response = client.post(
        f"/api/v1/departments/{department_id}/teams",
        json={"name": "Backend", "description": None},
    )
    team_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/teams/{team_id}",
        json={
            "name": "Platform",
            "description": "Plattform-Entwicklung",
        },
    )
    delete_response = client.delete(f"/api/v1/teams/{team_id}")
    get_response = client.get(f"/api/v1/teams/{team_id}")

    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Platform"
    assert delete_response.status_code == 204
    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_create_team_rejects_whitespace_name(
    client: TestClient,
) -> None:
    department_response = client.post(
        "/api/v1/departments",
        json={"name": "Entwicklung", "description": None},
    )
    department_id = department_response.json()["id"]

    response = client.post(
        f"/api/v1/departments/{department_id}/teams",
        json={"name": "   ", "description": None},
    )

    assert response.status_code == 422
    assert "name must not be empty" in response.json()["detail"]
