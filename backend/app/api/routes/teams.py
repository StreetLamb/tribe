from typing import Any
from sqlmodel import func, select
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.graph.build import generator
from app.api.deps import CurrentUser, SessionDep
from app.models import Member, TeamChat, TeamsOut, TeamCreate, TeamUpdate, TeamOut, Team, Message

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
                "tools": []
            },
            "MalayFoodExpert": {
                "type": "worker",
                "name": "MalayFoodExpert",
                "backstory": "Studied culinary school in Singapore. Well-verse in hawker to fine-dining experiences. INTP.",
                "role": "Provide malay food suggestions in Singapore",
                "tools": []
            },
        }
    },
    "TravelExpertLeader": {
        "name": "TravelKakis",
        "members": {
            "FoodExpertLeader": {
                "type": "leader",
                "name": "FoodExpertLeader",
                "role": "Gather inputs from your team and provide a diverse food suggestions in Singapore.",
                "tools": []
            },
            "HistoryExpert": {
                "type": "worker",
                "name": "HistoryExpert",
                "backstory": "Studied Singapore history. Well-verse in Singapore architecture. INTJ.",
                "role": "Provide places to sight-see with a history/architecture angle",
                "tools": []
            }
        }
    }
}
team_leader = "TravelExpertLeader"

router = APIRouter()

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
    *, session: SessionDep, current_user: CurrentUser, team_in: TeamCreate
) -> Any:
    """
    Create new team and it's team leader
    """
    team = Team.model_validate(team_in, update={"owner_id": current_user.id})
    session.add(team)
    session.commit()
    
    # Create team leader
    member= Member(**{'name': 'Team Leader', 'type': 'root', 'role': 'Gather inputs from your team and answer the question.', 'owner_of': team.id, 'position_x': 0, 'position_y': 0, "belongs_to": team.id})
    session.add(member)
    session.commit()
    
    return team

@router.put("/{id}", response_model=TeamOut)
def update_team(
    *, session: SessionDep, current_user: CurrentUser, id: int, team_in: TeamUpdate
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

@router.post("/{id}/stream")
async def stream(session: SessionDep, current_user: CurrentUser, id: int, team_chat: TeamChat):
    """
    Stream a response to a user's input.
    """
    team = session.get(Team, id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if not current_user.is_superuser and (team.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return StreamingResponse(generator(team, team.members, team_chat.messages), media_type="text/event-stream")