from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import Settings
from app.models import Team, TeamCreate
from app.tests.utils.utils import random_lower_string


def create_team(db: Session, user_id: int) -> Team:
    team_data = {
        "name": random_lower_string(),
        "description": None,
        "workflow": "sequential",  # assuming a valid workflow
        "owner_id": user_id,
    }
    team = Team.model_validate(TeamCreate(**team_data), update={"owner_id": user_id})
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def test_read_teams(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_team(db, 0)
    response = client.get(
        f"{Settings.API_V1_STR}/teams", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "results" in data
    assert data["count"] == 1
    assert len(data["results"]) == 1


def test_read_team(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    team = create_team(db, 0)
    response = client.get(
        f"{Settings.API_V1_STR}/teams/{team.id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == team.name


def test_create_team(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    team_data = {
        "name": random_lower_string(),
        "description": random_lower_string(),
        "workflow": "sequential",
    }
    response = client.post(
        f"{Settings.API_V1_STR}/teams", json=team_data, headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == team_data["name"]
    assert data["description"] == team_data["description"]


def test_create_team_duplicate_name(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    team = create_team(db, 0)
    duplicate_team_data = {
        "name": team.name,
        "description": random_lower_string(),
        "workflow": "sequential",
    }
    response = client.post(
        f"{Settings.API_V1_STR}/teams",
        json=duplicate_team_data,
        headers=superuser_token_headers,
    )
    assert response.status_code == 400


def test_update_team(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    team = create_team(db, 0)
    updated_team_data = {"name": random_lower_string()}
    response = client.put(
        f"{Settings.API_V1_STR}/teams/{team.id}",
        json=updated_team_data,
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == updated_team_data["name"]


def test_delete_team(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    team = create_team(db, 0)
    response = client.delete(
        f"{Settings.API_V1_STR}/teams/{team.id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
