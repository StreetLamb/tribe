from app.core.models.skill import Skill
from app.core.models.team import Team
from pydantic import Field
from sqlmodel import Relationship, SQLModel


class MemberSkillsLink(SQLModel, table=True):
    member_id: int | None = Field(default=None, foreign_key="member.id", primary_key=True)
    skill_id: int | None = Field(default=None, foreign_key="skill.id", primary_key=True)

class MemberBase(SQLModel):
    name: str
    backstory: str | None = None
    role: str
    type: str
    owner_of: int | None = int
class MemberCreate(MemberBase):
    name: str

class MemberUpdate(MemberBase):
    name: str | None = None
    backstory: str | None = None
    role: str | None = None
    type: str | None = None
    belongs_to: int | None = None
    
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