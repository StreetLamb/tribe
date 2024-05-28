from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import Member, MemberCreate, Team, TeamCreate
from app.tests.utils.utils import random_lower_string


def create_team(db: Session, user_id: int) -> Team:
    team_data = {
        "name": random_lower_string(),
        "description": None,
        "workflow": "sequential",  # assuming a valid workflow
        "owner_id": user_id,
    }
    team = Team.model_validate(TeamCreate(**team_data))
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def test_read_members(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/members", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "data" in data


def test_read_member(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    team = create_team(db, 0)
    member_data = {
        "name": random_lower_string(),
        "backstory": None,
        "role": "worker",
        "type": "worker",
        "owner_of": None,
        "position_x": 0.0,
        "position_y": 0.0,
        "source": None,
        "provider": "ChatOpenAI",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "interrupt": False,
        "belongs_to": team.id,
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
    assert data["name"] == member_data["name"]
    assert data["role"] == member_data["role"]
    assert data["type"] == member_data["type"]


def test_create_member(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    team = create_team(db, 0)
    member_data = {
        "name": random_lower_string(),
        "backstory": None,
        "role": "worker",
        "type": "worker",
        "owner_of": None,
        "position_x": 0.0,
        "position_y": 0.0,
        "source": None,
        "provider": "ChatOpenAI",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "interrupt": False,
        "belongs_to": team.id,
    }
    response = client.post(
        f"{settings.API_V1_STR}/members",
        json=member_data,
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == member_data["name"]
    assert data["role"] == member_data["role"]
    assert data["type"] == member_data["type"]


def test_create_member_duplicate_name(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    team = create_team(db, 0)
    member_data = {
        "name": random_lower_string(),
        "backstory": None,
        "role": "worker",
        "type": "worker",
        "owner_of": None,
        "position_x": 0.0,
        "position_y": 0.0,
        "source": None,
        "provider": "ChatOpenAI",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "interrupt": False,
        "belongs_to": team.id,
    }
    member = Member.model_validate(MemberCreate(**member_data))
    db.add(member)
    db.commit()
    db.refresh(member)

    duplicate_member_data = {
        "name": member.name,
        "backstory": None,
        "role": "worker",
        "type": "worker",
        "owner_of": None,
        "position_x": 0.0,
        "position_y": 0.0,
        "source": None,
        "provider": "ChatOpenAI",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "interrupt": False,
        "belongs_to": team.id,
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
    team = create_team(db, 0)
    member_data = {
        "name": random_lower_string(),
        "backstory": None,
        "role": "worker",
        "type": "worker",
        "owner_of": None,
        "position_x": 0.0,
        "position_y": 0.0,
        "source": None,
        "provider": "ChatOpenAI",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "interrupt": False,
        "belongs_to": team.id,
    }
    member = Member.model_validate(MemberCreate(**member_data))
    db.add(member)
    db.commit()
    db.refresh(member)

    updated_member_data = {
        "name": random_lower_string(),
        "backstory": None,
        "role": "worker",
        "type": "worker",
        "owner_of": None,
        "position_x": 0.0,
        "position_y": 0.0,
        "source": None,
        "provider": "ChatOpenAI",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "interrupt": False,
        "belongs_to": team.id,
    }
    response = client.put(
        f"{settings.API_V1_STR}/members/{member.id}",
        json=updated_member_data,
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == updated_member_data["name"]
    assert data["role"] == updated_member_data["role"]
    assert data["type"] == updated_member_data["type"]


def test_update_member_duplicate_name(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    team = create_team(db, 0)
    member_data = {
        "name": random_lower_string(),
        "backstory": None,
        "role": "worker",
        "type": "worker",
        "owner_of": None,
        "position_x": 0.0,
        "position_y": 0.0,
        "source": None,
        "provider": "ChatOpenAI",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "interrupt": False,
        "belongs_to": team.id,
    }
    member = Member.model_validate(MemberCreate(**member_data))
    db.add(member)
    db.commit()
    db.refresh(member)

    another_member_data = {
        "name": random_lower_string(),
        "backstory": None,
        "role": "worker",
        "type": "worker",
        "owner_of": None,
        "position_x": 0.0,
        "position_y": 0.0,
        "source": None,
        "provider": "ChatOpenAI",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "interrupt": False,
        "belongs_to": team.id,
    }
    another_member = Member.model_validate(MemberCreate(**another_member_data))
    db.add(another_member)
    db.commit()
    db.refresh(another_member)

    duplicate_member_data = {
        "name": another_member.name,
        "backstory": None,
        "role": "worker",
        "type": "worker",
        "owner_of": None,
        "position_x": 0.0,
        "position_y": 0.0,
        "source": None,
        "provider": "ChatOpenAI",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "interrupt": False,
        "belongs_to": team.id,
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
    team = create_team(db, 0)
    member_data = {
        "name": random_lower_string(),
        "backstory": None,
        "role": "worker",
        "type": "worker",
        "owner_of": None,
        "position_x": 0.0,
        "position_y": 0.0,
        "source": None,
        "provider": "ChatOpenAI",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "interrupt": False,
        "belongs_to": team.id,
    }
    member = Member.model_validate(MemberCreate(**member_data))
    db.add(member)
    db.commit()
    db.refresh(member)

    response = client.delete(
        f"{settings.API_V1_STR}/members/{member.id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
