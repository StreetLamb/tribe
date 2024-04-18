from enum import Enum
from typing import List
from pydantic import BaseModel
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
    items: list["Item"] = Relationship(back_populates="owner")
    teams: list["Team"] = Relationship(back_populates="owner")


# Properties to return via API, id is always required
class UserOut(UserBase):
    id: int


class UsersOut(SQLModel):
    data: list[UserOut]
    count: int








# ==============ITEM=========================

# Shared properties
class ItemBase(SQLModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    title: str


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = None  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemOut(ItemBase):
    id: int
    owner_id: int


class ItemsOut(SQLModel):
    data: list[ItemOut]
    count: int








# ==============TEAM=========================

class TeamBase(SQLModel):
    name: str
    description: str | None = None

class TeamCreate(TeamBase):
    name: str

class TeamUpdate(TeamBase):
    name: str | None = None
    
class ChatMessageType(str, Enum):
    human = "human"
    ai = "ai"

class ChatMessage(BaseModel):
    type: ChatMessageType
    content: str
    
class TeamChat(BaseModel):
    messages: List[ChatMessage]

class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="teams")
    members: list["Member"] = Relationship(back_populates="belongs", sa_relationship_kwargs={"cascade": "delete"})
    
# Properties to return via API, id is always required
class TeamOut(TeamBase):
    id: int
    owner_id: int


class TeamsOut(SQLModel):
    data: list[TeamOut]
    count: int








# ==============MEMBER=========================

class MemberSkillsLink(SQLModel, table=True):
    member_id: int | None = Field(default=None, foreign_key="member.id", primary_key=True)
    skill_id: int | None = Field(default=None, foreign_key="skill.id", primary_key=True)

class MemberBase(SQLModel):
    name: str
    backstory: str | None = None
    role: str
    type: str
    owner_of: int | None = None
    position_x: float
    position_y: float
    source: int | None = None
    
class MemberCreate(MemberBase):
    name: str

class MemberUpdate(MemberBase):
    name: str | None = None
    backstory: str | None = None
    role: str | None = None
    type: str | None = None
    belongs_to: int | None = None
    position_x: float | None = None
    position_y: float | None = None
    
    
class Member(MemberBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    belongs_to: int | None = Field(default=None, foreign_key="team.id", nullable=False)
    belongs: Team | None = Relationship(back_populates="members")
    skills: list["Skill"] = Relationship(back_populates="members", link_model=MemberSkillsLink)
    
class MemberOut(MemberBase):
    id: int
    belongs_to: int
    owner_of: int | None


class MembersOut(SQLModel):
    data: list[MemberOut]
    count: int








# ===============SKILL========================

class SkillBase(SQLModel):
    name: str
    description: str | None = None

class SkillCreate(SkillBase):
    name: str

class SkillUpdate(SkillBase):
    name: str | None = None
    description: str | None = None

class Skill(SkillBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    members: list["Member"] = Relationship(back_populates="skills", link_model=MemberSkillsLink)