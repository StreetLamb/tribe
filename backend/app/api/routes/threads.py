from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Team,
    Thread,
    ThreadCreate,
    ThreadOut,
    ThreadsOut,
    ThreadUpdate,
)

router = APIRouter()


@router.get("/", response_model=ThreadsOut)
def read_threads(
    session: SessionDep,
    current_user: CurrentUser,
    team_id: int,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve threads
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Thread)
        count = session.exec(count_statement).one()
        statement = (
            select(Thread).where(Thread.team_id == team_id).offset(skip).limit(limit)
        )
        teams = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Thread)
            .join(Team)
            .where(Team.owner_id == current_user.id, Thread.team_id == team_id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Thread)
            .join(Team)
            .where(Team.owner_id == current_user.id, Thread.team_id == team_id)
            .offset(skip)
            .limit(limit)
        )
        teams = session.exec(statement).all()
    return ThreadsOut(data=teams, count=count)


@router.get("/{id}", response_model=ThreadOut)
def read_thread(
    session: SessionDep, current_user: CurrentUser, team_id: int, id: int
) -> Any:
    """
    Get thread by ID.
    """
    if current_user.is_superuser:
        statement = (
            select(Thread).join(Team).where(Thread.id == id, Thread.team_id == team_id)
        )
        thread = session.exec(statement).first()
    else:
        statement = (
            select(Thread)
            .join(Team)
            .where(
                Thread.id == id,
                Thread.team_id == team_id,
                Team.owner_id == current_user.id,
            )
        )
        thread = session.exec(statement).first()

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread


@router.post("/", response_model=ThreadOut)
def create_thread(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: int,
    thread_in: ThreadCreate,
) -> Any:
    """
    Create new thread
    """
    if not current_user.is_superuser:
        team = session.get(Team, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found.")
        if team.owner_id != current_user.id:
            raise HTTPException(status_code=400, detail="Not enough permissions")
    thread = Thread.model_validate(thread_in, update={"team_id": team_id})
    session.add(thread)
    session.commit()
    session.refresh(thread)
    return thread


@router.put("/{id}", response_model=ThreadOut)
def update_team(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: int,
    id: int,
    thread_in: ThreadUpdate,
) -> Any:
    """
    Update a thread.
    """
    if current_user.is_superuser:
        statement = (
            select(Thread).join(Team).where(Thread.id == id, Thread.team_id == team_id)
        )
        thread = session.exec(statement).first()
    else:
        statement = (
            select(Thread)
            .join(Team)
            .where(
                Thread.id == id,
                Thread.team_id == team_id,
                Team.owner_id == current_user.id,
            )
        )
        thread = session.exec(statement).first()

    if not thread:
        raise HTTPException(status_code=404, detail="Member not found")

    update_dict = thread_in.model_dump(exclude_unset=True)
    thread.sqlmodel_update(update_dict)
    session.add(thread)
    session.commit()
    session.refresh(thread)
    return thread


@router.delete("/{id}")
def delete_thread(
    session: SessionDep, current_user: CurrentUser, team_id: int, id: int
) -> Any:
    """
    Delete a thread.
    """
    if current_user.is_superuser:
        statement = (
            select(Thread).join(Team).where(Thread.id == id, Thread.team_id == team_id)
        )
        thread = session.exec(statement).first()
    else:
        statement = (
            select(Thread)
            .join(Team)
            .where(
                Thread.id == id,
                Thread.team_id == team_id,
                Team.owner_id == current_user.id,
            )
        )
        thread = session.exec(statement).first()

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    session.delete(thread)
    session.commit()
    return Message(message="Thread deleted successfully")
