from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import Member, MemberCreate
from app.tests.utils.utils import random_email, random_lower_string


def test_read_members(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/members", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "results" in data


def test_read_member(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    member_data = {
        "email": random_email(),
        "name": random_lower_string(),
        "team_id": None,
    }
    member = Member.model_validate(MemberCreate(**member_data))
    db.add(member)
    db.commit()
    db.refresh(member)

    response = client.get(
        f"{settings.API_V1_STR}/members/{member.id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == member_data["email"]
    assert data["name"] == member_data["name"]
    assert data["team_id"] == member_data["team_id"]


def test_create_member(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    member_data = {
        "email": random_email(),
        "name": random_lower_string(),
        "team_id": None,
    }
    response = client.post(
        f"{settings.API_V1_STR}/members",
        json=member_data,
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == member_data["email"]
    assert data["name"] == member_data["name"]
    assert data["team_id"] == member_data["team_id"]


def test_create_member_duplicate_name(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    member_data = {
        "email": random_email(),
        "name": random_lower_string(),
        "team_id": None,
    }
    member = Member.model_validate(MemberCreate(**member_data))
    db.add(member)
    db.commit()
    db.refresh(member)

    duplicate_member_data = {
        "email": random_email(),
        "name": member.name,
        "team_id": None,
    }
    response = client.post(
        f"{settings.API_V1_STR}/members",
        json=duplicate_member_data,
        headers=superuser_token_headers,
    )
    assert response.status_code == 400


def test_update_member(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    member_data = {
        "email": random_email(),
        "name": random_lower_string(),
        "team_id": None,
    }
    member = Member.model_validate(MemberCreate(**member_data))
    db.add(member)
    db.commit()
    db.refresh(member)

    updated_member_data = {
        "email": random_email(),
        "name": random_lower_string(),
        "team_id": None,
    }
    response = client.put(
        f"{settings.API_V1_STR}/members/{member.id}",
        json=updated_member_data,
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == updated_member_data["email"]
    assert data["name"] == updated_member_data["name"]
    assert data["team_id"] == updated_member_data["team_id"]


def test_update_member_duplicate_name(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    member_data = {
        "email": random_email(),
        "name": random_lower_string(),
        "team_id": None,
    }
    member = Member.model_validate(MemberCreate(**member_data))
    db.add(member)
    db.commit()
    db.refresh(member)

    another_member_data = {
        "email": random_email(),
        "name": random_lower_string(),
        "team_id": None,
    }
    another_member = Member.model_validate(MemberCreate(**another_member_data))
    db.add(another_member)
    db.commit()
    db.refresh(another_member)

    duplicate_member_data = {
        "email": random_email(),
        "name": another_member.name,
        "team_id": None,
    }
    response = client.put(
        f"{settings.API_V1_STR}/members/{member.id}",
        json=duplicate_member_data,
        headers=superuser_token_headers,
    )
    assert response.status_code == 400


def test_delete_member(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    member_data = {
        "email": random_email(),
        "name": random_lower_string(),
        "team_id": None,
    }
    member = Member.model_validate(MemberCreate(**member_data))
    db.add(member)
    db.commit()
    db.refresh(member)

    response = client.delete(
        f"{settings.API_V1_STR}/members/{member.id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
