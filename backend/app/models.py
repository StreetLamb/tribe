from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic import Field as PydanticField
from sqlalchemy import DateTime, UniqueConstraint, func
from sqlmodel import Field, Relationship, SQLModel


class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: int | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str


# ===============USER========================


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# TODO replace email str with EmailStr when sqlmodel supports it
class UserCreateOpen(SQLModel):
    email: str
    password: str
    full_name: str | None = None


# Properties to receive via API on update, all are optional
# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdate(UserBase):
    email: str | None = None  # type: ignore
    password: str | None = None


# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdateMe(SQLModel):
    full_name: str | None = None
    email: str | None = None


class UpdatePassword(SQLModel):
    current_password: str
    new_password: str


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    teams: list["Team"] = Relationship(back_populates="owner")


# Properties to return via API, id is always required
class UserOut(UserBase):
    id: int


class UsersOut(SQLModel):
    data: list[UserOut]
    count: int


# ==============TEAM=========================


class TeamBase(SQLModel):
    name: str = PydanticField(pattern=r"^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = None


class TeamCreate(TeamBase):
    workflow: str


class TeamUpdate(TeamBase):
    name: str | None = PydanticField(pattern=r"^[a-zA-Z0-9_-]{1,64}$", default=None)  # type: ignore[assignment]


class ChatMessageType(str, Enum):
    human = "human"
    ai = "ai"


class ChatMessage(BaseModel):
    type: ChatMessageType
    content: str


class TeamChat(BaseModel):
    messages: list[ChatMessage]


class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(regex=r"^[a-zA-Z0-9_-]{1,64}$", unique=True)
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="teams")
    members: list["Member"] = Relationship(
        back_populates="belongs", sa_relationship_kwargs={"cascade": "delete"}
    )
    workflow: str  # TODO: This should be an enum 'sequential' and 'hierarchical'
    threads: list["Thread"] = Relationship(
        back_populates="team", sa_relationship_kwargs={"cascade": "delete"}
    )


# Properties to return via API, id is always required
class TeamOut(TeamBase):
    id: int
    owner_id: int
    workflow: str


class TeamsOut(SQLModel):
    data: list[TeamOut]
    count: int


# =============Threads===================


class ThreadBase(SQLModel):
    query: str


class ThreadCreate(ThreadBase):
    pass


class ThreadUpdate(ThreadBase):
    query: str | None
    updated_at: datetime | None


class Thread(ThreadBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    thread_id: str | None = Field(nullable=False)
    updated_at: datetime = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"onupdate": func.now(), "server_default": func.now()},
    )
    team_id: int | None = Field(default=None, foreign_key="team.id", nullable=False)
    team: Team | None = Relationship(back_populates="threads")


class ThreadOut(SQLModel):
    id: str
    thread_id: str
    query: str
    updated_at: datetime


class ThreadsOut(SQLModel):
    data: list[ThreadOut]
    count: int


# ==============MEMBER=========================


class MemberSkillsLink(SQLModel, table=True):
    member_id: int | None = Field(
        default=None, foreign_key="member.id", primary_key=True
    )
    skill_id: int | None = Field(default=None, foreign_key="skill.id", primary_key=True)


class MemberBase(SQLModel):
    name: str = PydanticField(pattern=r"^[a-zA-Z0-9_-]{1,64}$")
    backstory: str | None = None
    role: str
    type: str  # one of: leader, worker, freelancer
    owner_of: int | None = None
    position_x: float
    position_y: float
    source: int | None = None
    provider: str = "ChatOpenAI"
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    interrupt: bool = False


class MemberCreate(MemberBase):
    pass


class MemberUpdate(MemberBase):
    name: str | None = PydanticField(pattern=r"^[a-zA-Z0-9_-]{1,64}$", default=None)  # type: ignore[assignment]
    backstory: str | None = None
    role: str | None = None  # type: ignore[assignment]
    type: str | None = None  # type: ignore[assignment]
    belongs_to: int | None = None
    position_x: float | None = None  # type: ignore[assignment]
    position_y: float | None = None  # type: ignore[assignment]
    skills: list["Skill"] | None = None
    provider: str | None = None  # type: ignore[assignment]
    model: str | None = None  # type: ignore[assignment]
    temperature: float | None = None  # type: ignore[assignment]
    interrupt: bool | None = None  # type: ignore[assignment]


class Member(MemberBase, table=True):
    __table_args__ = (
        UniqueConstraint("name", "belongs_to", name="unique_team_and_name"),
    )
    id: int | None = Field(default=None, primary_key=True)
    belongs_to: int | None = Field(default=None, foreign_key="team.id", nullable=False)
    belongs: Team | None = Relationship(back_populates="members")
    skills: list["Skill"] = Relationship(
        back_populates="members", link_model=MemberSkillsLink
    )


class MemberOut(MemberBase):
    id: int
    belongs_to: int
    owner_of: int | None
    skills: list["Skill"]


class MembersOut(SQLModel):
    data: list[MemberOut]
    count: int


# ===============SKILL========================


class SkillBase(SQLModel):
    name: str
    description: str | None = None


class Skill(SkillBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    members: list["Member"] = Relationship(
        back_populates="skills", link_model=MemberSkillsLink
    )


class SkillsOut(SQLModel):
    data: list[Skill]
    count: int


class SkillOut(SkillBase):
    id: int
    description: str | None
