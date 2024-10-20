from typing import Any
from uuid import UUID

from fastapi import APIRouter
from sqlalchemy import func
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models.user import User, UserPublic, UsersPublic

router = APIRouter()


@router.get("", response_model=UsersPublic)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)


@router.get("/me", response_model=UserPublic)
def read_current_user(current_user: CurrentUser) -> Any:
    return current_user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    user = session.get(User, user_id)
    if user == current_user:
        return user

    return user
