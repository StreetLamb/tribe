from app.core.models.member import Member
from app.core.models.user import User
from pydantic import BaseModel, Field
from sqlmodel import Relationship, SQLModel


class TeamBase(SQLModel):
    name: str
    description: str | None = None

class TeamCreate(TeamBase):
    name: str

class TeamUpdate(TeamBase):
    name: str | None = None
    
class TeamChat(BaseModel):
    message: str

class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="teams")
    members: list["Member"] = Relationship(back_populates="belongs")
    
# Properties to return via API, id is always required
class TeamOut(TeamBase):
    id: int
    owner_id: int


class TeamsOut(SQLModel):
    data: list[TeamOut]
    count: int