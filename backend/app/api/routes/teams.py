from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.core.graph.build import generator
from app.models import (
    Member,
    Message,
    Team,
    TeamChat,
    TeamCreate,
    TeamOut,
    TeamsOut,
    TeamUpdate,
)

# TODO: To remove
teams = {
    "FoodExpertLeader": {
        "name": "FoodExperts",
        "members": {
            "ChineseFoodExpert": {
                "type": "worker",
                "name": "ChineseFoodExpert",
                "backstory": "Studied culinary school in Singapore. Well-verse in hawker to fine-dining experiences. ISFP.",
                "role": "Provide chinese food suggestions in Singapore",
                "tools": [],
            },
            "MalayFoodExpert": {
                "type": "worker",
                "name": "MalayFoodExpert",
                "backstory": "Studied culinary school in Singapore. Well-verse in hawker to fine-dining experiences. INTP.",
                "role": "Provide malay food suggestions in Singapore",
                "tools": [],
            },
        },
    },
    "TravelExpertLeader": {
        "name": "TravelKakis",
        "members": {
            "FoodExpertLeader": {
                "type": "leader",
                "name": "FoodExpertLeader",
                "role": "Gather inputs from your team and provide a diverse food suggestions in Singapore.",
                "tools": [],
            },
            "HistoryExpert": {
                "type": "worker",
                "name": "HistoryExpert",
                "backstory": "Studied Singapore history. Well-verse in Singapore architecture. INTJ.",
                "role": "Provide places to sight-see with a history/architecture angle",
                "tools": [],
            },
        },
    },
}
team_leader = "TravelExpertLeader"

router = APIRouter()


async def check_duplicate_name_on_create(
    session: SessionDep, team_in: TeamCreate
) -> None:
    """Validate that team name is unique"""
    statement = select(Team).where(Team.name == team_in.name)
    team = session.exec(statement).first()
    if team:
        raise HTTPException(status_code=400, detail="Team name already exists")


async def check_duplicate_name_on_update(
    session: SessionDep, team_in: TeamUpdate, id: int
) -> None:
    """Validate that team name is unique"""
    statement = select(Team).where(Team.name == team_in.name, Team.id != id)
    team = session.exec(statement).first()
    if team:
        raise HTTPException(status_code=400, detail="Team name already exists")


@router.get("/", response_model=TeamsOut)
def read_teams(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve teams
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Team)
        count = session.exec(count_statement).one()
        statement = select(Team).offset(skip).limit(limit)
        teams = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Team)
            .where(Team.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Team)
            .where(Team.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        teams = session.exec(statement).all()
    return TeamsOut(data=teams, count=count)


@router.get("/{id}", response_model=TeamOut)
def read_team(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get team by ID.
    """
    team = session.get(Team, id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if not current_user.is_superuser and (team.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return team


@router.post("/", response_model=TeamOut)
def create_team(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_in: TeamCreate,
    _: bool = Depends(check_duplicate_name_on_create),
) -> Any:
    """
    Create new team and it's team leader
    """
    team = Team.model_validate(team_in, update={"owner_id": current_user.id})
    if team.workflow not in ["hierarchical", "sequential"]:
        raise HTTPException(status_code=400, detail="Invalid workflow")
    session.add(team)
    session.commit()

    if team.workflow == "hierarchical":
        # Create team leader
        member = Member(
            # The leader name will be used as the team's name in the graph, so it has to be specific
            name=f"{team.name}Leader",
            type="root",
            role="Gather inputs from your team and answer the question.",
            owner_of=team.id,
            position_x=0,
            position_y=0,
            belongs_to=team.id,
        )
    else:
        # Create a freelancer head
        member = Member(
            name="Worker0",
            type="freelancer_root",
            role="Answer the user's question.",
            owner_of=None,
            position_x=0,
            position_y=0,
            belongs_to=team.id,
        )
    session.add(member)
    session.commit()

    return team


@router.put("/{id}", response_model=TeamOut)
def update_team(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    team_in: TeamUpdate,
    _: bool = Depends(check_duplicate_name_on_update),
) -> Any:
    """
    Update a team.
    """
    team = session.get(Team, id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if not current_user.is_superuser and (team.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = team_in.model_dump(exclude_unset=True)
    team.sqlmodel_update(update_dict)
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@router.delete("/{id}")
def delete_team(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Delete a team.
    """
    team = session.get(Team, id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if not current_user.is_superuser and (team.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(team)
    session.commit()
    return Message(message="Team deleted successfully")


@router.post("/{id}/stream/{thread_id}")
async def stream(
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    thread_id: str,
    team_chat: TeamChat,
) -> StreamingResponse:
    """
    Stream a response to a user's input.
    """
    # Get team and join members and skills
    team = session.get(Team, id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if not current_user.is_superuser and (team.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Populate the skills for each member
    members = team.members
    for member in members:
        member.skills = member.skills

    return StreamingResponse(
        generator(team, members, team_chat.messages, thread_id),
        media_type="text/event-stream",
    )
