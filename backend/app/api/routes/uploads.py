from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Upload,
    UploadCreate,
    UploadOut,
    UploadsOut,
    UploadUpdate,
)

router = APIRouter()


@router.get("/", response_model=UploadsOut)
def read_uploads(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve uploads.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Upload)
        statement = select(Upload).offset(skip).limit(limit)
    else:
        count_statement = (
            select(func.count())
            .select_from(Upload)
            .where(Upload.owner_id == current_user.id)
        )
        statement = (
            select(Upload)
            .where(Upload.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )

    count = session.exec(count_statement).one()
    uploads = session.exec(statement).all()

    return UploadsOut(data=uploads, count=count)


@router.post("/", response_model=UploadOut)
def create_upload(
    session: SessionDep,
    current_user: CurrentUser,
    name: Annotated[str, Form()],
    file: UploadFile,
) -> Any:
    """Create upload"""
    # TODO: Handle file upload and retrieve the path
    upload = Upload.model_validate(
        UploadCreate(name=name), update={"owner_id": current_user.id, "path": ""}
    )
    session.add(upload)
    session.commit()
    return upload


@router.put("/{id}", response_model=UploadOut)
def update_upload(
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    name: Annotated[str | None, Form()],
    file: UploadFile = File(None),
) -> Any:
    """Update upload"""
    upload = session.get(Upload, id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    if not current_user.is_superuser and upload.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    # TODO: Handle file upload and retrieve the path
    update_dict = UploadUpdate(name=name, last_modified=datetime.now()).model_dump(
        exclude_unset=True
    )
    upload.sqlmodel_update(update_dict)
    session.add(upload)
    session.commit()
    session.refresh(upload)
    return upload


@router.delete("/{id}")
def delete_upload(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    upload = session.get(Upload, id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    if not current_user.is_superuser and upload.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(upload)
    session.commit()
    return Message(message="Upload deleted successfully")
