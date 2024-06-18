from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.core.graph.skills import managed_skills
from app.models import Skill, User, UserCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # from app.core.engine import engine
    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)

    existing_skills = session.exec(select(Skill)).all()
    existing_skills_dict = {skill.name: skill for skill in existing_skills}

    current_skill_names = set(managed_skills.keys())

    # Add or update skills in the database
    for skill_name, skill_info in managed_skills.items():
        if skill_name in existing_skills_dict:
            existing_skill = existing_skills_dict[skill_name]
            if existing_skill.description != skill_info.description:
                # Update the existing skill's description
                existing_skill.description = skill_info.description
                session.add(existing_skill)  # Mark the modified object for saving
        else:
            new_skill = Skill(
                name=skill_name,
                description=skill_info.description,
                managed=True,
                owner_id=user.id,
            )
            session.add(new_skill)  # Prepare new skill for addition to the database

    # Delete skills that are no longer in the current code and are managed
    for skill_name in existing_skills_dict:
        if (
            skill_name not in current_skill_names
            and existing_skills_dict[skill_name].managed
        ):
            skill_to_delete = existing_skills_dict[skill_name]
            session.delete(skill_to_delete)

    session.commit()
