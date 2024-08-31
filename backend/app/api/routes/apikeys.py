from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.core.security import generate_apikey, generate_short_apikey, get_password_hash
from app.models import ApiKey, ApiKeyIn, ApiKeyOut, Team

router = APIRouter()


@router.post("/", response_model=ApiKeyOut)
def create_api_key(
    session: SessionDep, current_user: CurrentUser, team_id: int, apikey_in: ApiKeyIn
) -> Any:
    """Create API key for a team."""

    # Check if the current user is not a superuser
    if not current_user.is_superuser:
        # Validate the provided team_id and check ownership
        team = session.get(Team, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found.")
        if team.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions.")

    # Generate API key and hash it
    key = generate_apikey()
    hashed_key = get_password_hash(key)
    short_key = generate_short_apikey(key)

    # Create the API key object
    apikey_data = apikey_in.model_dump()
    apikey = ApiKey(
        **apikey_data,
        team_id=team_id,
        hashed_key=hashed_key,
        short_key=short_key,
    )

    # Save the new API key to the database
    session.add(apikey)
    session.commit()
    session.refresh(apikey)

    return ApiKeyOut(
        id=apikey.id,
        description=apikey.description,
        key=key,
        created_at=apikey.created_at,
    )
