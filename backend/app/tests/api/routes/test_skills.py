from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import Skill
from app.tests.utils.utils import random_lower_string


def create_skill(db: Session) -> Skill:
    skill_data = {"name": random_lower_string(), "description": random_lower_string()}
    skill = Skill(**skill_data)
    db.add(skill)
    db.commit()
    return skill


def test_read_skills(client: TestClient, db: Session) -> None:
    create_skill(db)
    response = client.get(f"{settings.API_V1_STR}/skills")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "data" in data


def test_read_skill(client: TestClient, db: Session) -> None:
    skill = create_skill(db)

    response = client.get(f"{settings.API_V1_STR}skills/{skill.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == skill.name
    assert data["description"] == skill.description
