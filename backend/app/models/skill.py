from app.core.models.member import Member, MemberSkillsLink
from pydantic import Field
from sqlmodel import Relationship, SQLModel


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