from fastapi import APIRouter

from app.api.routes import items, login, members, users, utils, teams

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(members.router, prefix="/teams/{team_id}/members", tags=["members"])
