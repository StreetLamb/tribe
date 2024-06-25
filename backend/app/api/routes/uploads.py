from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import IO, Annotated, Any

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from sqlmodel import func, select
from starlette import status

from app.api.deps import CurrentUser, SessionDep
from app.core.graph.rag.qdrant import QdrantStore
from app.models import (
    Message,
    Upload,
    UploadCreate,
    UploadOut,
    UploadsOut,
    UploadUpdate,
)

router = APIRouter()


async def valid_content_length(
    content_length: int = Header(..., lt=50 * 1024 * 1024),
) -> int:
    return content_length


def save_file_if_within_size_limit(file: UploadFile, file_size: int) -> IO[bytes]:
    """
    Check if the uploaded file size is smaller than the specified file size.
    This is to restrict an attacker from sending a valid Content-Length header and a
    body bigger than what the app can take.
    If the file size exceeds the limit, raise an HTTP 413 error. Otherwise, save the file
    to a temporary location and return the temporary file.

    Args:
        file (UploadFile): The file uploaded by the user.
        file_size (int): The file size in bytes.

    Raises:
        HTTPException: If the file size exceeds the maximum allowed size.

    Returns:
        IO: A temporary file containing the uploaded data.
    """
    # Check file size
    real_file_size = 0
    temp: IO[bytes] = NamedTemporaryFile(delete=False)
    for chunk in file.file:
        real_file_size += len(chunk)
        if real_file_size > file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Too large"
            )
        temp.write(chunk)
    temp.close()
    return temp


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
    description: Annotated[str, Form()],
    file: UploadFile,
    chunk_size: Annotated[int, Form(ge=0)],
    chunk_overlap: Annotated[int, Form(ge=0)],
    file_size: int = Depends(valid_content_length),
) -> Any:
    """Create upload"""
    if file.content_type not in ["application/pdf"]:
        raise HTTPException(status_code=400, detail="Invalid document type")

    temp_file = save_file_if_within_size_limit(file, file_size)
    upload = Upload.model_validate(
        UploadCreate(name=name, description=description),
        update={"owner_id": current_user.id},
    )
    session.add(upload)
    session.commit()

    try:
        # To appease type-checking. This should never happen.
        if current_user.id is None or upload.id is None:
            raise HTTPException(
                status_code=500, detail="Failed to retrieve user and upload ID"
            )
        QdrantStore().create(
            temp_file.name, upload.id, current_user.id, chunk_size, chunk_overlap
        )
    except Exception as e:
        session.delete(upload)
        session.commit()
        raise e

    return upload


@router.put("/{id}", response_model=UploadOut)
def update_upload(
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    name: str | None = Form(None),
    description: str | None = Form(None),
    chunk_size: Annotated[int, Form(ge=0)] | None = Form(None),
    chunk_overlap: Annotated[int, Form(ge=0)] | None = Form(None),
    file: UploadFile | None = File(None),
    file_size: int = Depends(valid_content_length),
) -> Any:
    """Update upload"""
    upload = session.get(Upload, id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    if not current_user.is_superuser and upload.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data: dict[str, str | datetime] = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if update_data:
        update_data["last_modified"] = datetime.now()
        update_dict = UploadUpdate(**update_data).model_dump(exclude_unset=True)
        upload.sqlmodel_update(update_dict)
        session.add(upload)

    if file:
        if file.content_type not in ["application/pdf"]:
            raise HTTPException(status_code=400, detail="Invalid document type")
        temp_file = save_file_if_within_size_limit(file, file_size)
        if upload.owner_id is None:
            raise HTTPException(status_code=500, detail="Failed to retrieve owner ID")
        if chunk_overlap is None or chunk_size is None:
            raise HTTPException(
                status_code=400,
                detail="If file is provided, chunk size and chunk overlap must be provided.",
            )
        QdrantStore().delete(id, upload.owner_id)
        QdrantStore().create(
            temp_file.name, id, upload.owner_id, chunk_size, chunk_overlap
        )

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

    try:
        session.delete(upload)
        if upload.owner_id is None:
            raise HTTPException(status_code=500, detail="Failed to retrieve owner ID")
        QdrantStore().delete(id, upload.owner_id)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete upload") from e

    return Message(message="Upload deleted successfully")
