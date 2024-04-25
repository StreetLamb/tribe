from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import SessionDep
from app.models import (
    Skill,
    SkillOut,
    SkillsOut,
)

router = APIRouter()


@router.get("/", response_model=SkillsOut)
def read_skills(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve skills.
    """
    count_statement = select(func.count()).select_from(Skill)
    count = session.exec(count_statement).one()

    statement = select(Skill).offset(skip).limit(limit)
    items = session.exec(statement).all()

    return SkillsOut(data=items, count=count)


@router.get("/{id}", response_model=SkillOut)
def read_skill(session: SessionDep, id: int) -> Any:
    """
    Get skill by ID.
    """
    skill = session.get(Skill, id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill
