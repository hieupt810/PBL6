from fastapi import APIRouter

from app.api.routes import login, users

api_router = APIRouter()

api_router.include_router(login.router, prefix="/login", tags=["Login"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
