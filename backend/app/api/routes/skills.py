from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, or_, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Skill,
    SkillCreate,
    SkillOut,
    SkillsOut,
    SkillUpdate,
)

router = APIRouter()


@router.get("/", response_model=SkillsOut)
def read_skills(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve skills.
    """
    count_statement = (
        select(func.count())
        .select_from(Skill)
        .where(or_(Skill.managed is True, Skill.owner_id == current_user.id))
    )
    count = session.exec(count_statement).one()

    statement = select(Skill).order_by(Skill.id).offset(skip).limit(limit)
    skills = session.exec(statement).all()

    return SkillsOut(data=skills, count=count)


@router.get("/{id}", response_model=SkillOut)
def read_skill(session: SessionDep, id: int) -> Any:
    """
    Get skill by ID.
    """
    skill = session.get(Skill, id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    if not skill.managed and (skill.owner_id != id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return skill


@router.post("/", response_model=SkillOut)
def create_skill(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    skill_in: SkillCreate,
) -> Any:
    """
    Create new skill.
    """
    skill = Skill.model_validate(skill_in, update={"owner_id": current_user.id})
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


@router.put("/{id}", response_model=SkillOut)
def update_skill(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    skill_in: SkillUpdate,
) -> Any:
    """
    Update a skill.
    """
    skill = session.get(Skill, id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    if not current_user.is_superuser and (skill.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = skill_in.model_dump(exclude_unset=True)
    skill.sqlmodel_update(update_dict)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


@router.delete("/{id}")
def delete_skill(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Delete a skill.
    """
    skill = session.get(Skill, id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    if not current_user.is_superuser and (skill.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    if skill.managed:
        raise HTTPException(status_code=400, detail="Cannot delete managed skills")
    session.delete(skill)
    session.commit()
    return Message(message="Skill deleted successfully")
