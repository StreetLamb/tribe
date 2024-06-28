from io import BytesIO
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlmodel import Session

from app.core.config import settings
from app.core.graph.rag.qdrant import QdrantStore
from app.models import Upload, UploadCreate, UploadStatus
from app.tests.utils.utils import random_lower_string


def create_upload(db: Session, user_id: int) -> Upload:
    upload_data = {
        "name": random_lower_string(),
        "description": random_lower_string(),
        "owner_id": user_id,
    }
    upload = Upload.model_validate(
        UploadCreate(**upload_data),
        update={
            "owner_id": user_id,
            "status": UploadStatus.COMPLETED,
        },
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)
    return upload


def test_read_uploads(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_upload(db, 1)
    response = client.get(
        f"{settings.API_V1_STR}/uploads", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "data" in data


def test_read_uploads_status_filter(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create in progress upload
    upload = create_upload(db, 1)
    upload.status = UploadStatus.IN_PROGRESS
    db.add(upload)
    db.commit()

    response = client.get(
        f"{settings.API_V1_STR}/uploads",
        headers=superuser_token_headers,
        params={"status": UploadStatus.IN_PROGRESS.value},
    )
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "data" in data
    assert all(upload["status"] == UploadStatus.IN_PROGRESS for upload in data["data"])


def test_create_upload(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create mock PDF file data
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
    file = BytesIO(pdf_content)
    file.name = "test_file.pdf"

    data = {
        "name": random_lower_string(),
        "description": random_lower_string(),
        "chunk_size": str(1024),
        "chunk_overlap": str(256),
    }

    files = {"file": (file.name, file, "application/pdf")}

    # Mock the entire QdrantStore.add method
    with patch.object(QdrantStore, "add", return_value=None) as mock_add:
        response = client.post(
            f"{settings.API_V1_STR}/uploads",
            headers=superuser_token_headers,
            data=data,
            files=files,
        )

        assert response.status_code == 200
        json_response = response.json()
        assert "id" in json_response
        assert json_response["name"] == data["name"]
        assert json_response["description"] == data["description"]
        mock_add.assert_called_once()


def test_update_upload(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    upload = create_upload(db, 1)
    data = {
        "name": random_lower_string(),
        "description": random_lower_string(),
    }
    response = client.put(
        f"{settings.API_V1_STR}/uploads/{upload.id}",
        headers=superuser_token_headers,
        data=data,
    )
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["name"] == data["name"]
    assert json_response["description"] == data["description"]


def test_delete_upload(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    upload = create_upload(db, 1)
    upload_id = upload.id

    with patch.object(QdrantStore, "delete", return_value=None) as mock_delete:
        response = client.delete(
            f"{settings.API_V1_STR}/uploads/{upload.id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        json_response = response.json()
        assert json_response["message"] == "Upload deleted successfully"
        mock_delete.assert_called_once_with(upload.id, upload.owner_id)
        # Check that upload does not exist in db anymore
        db.expire_all()
        statement = select(Upload).where(Upload.id == upload_id)
        result = db.exec(statement)
        deleted_upload = result.first()
        assert deleted_upload is None
