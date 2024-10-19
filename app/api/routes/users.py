from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import func
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.helpers.user import create_user, get_user_by_email
from app.models.user import User, UserCreate, UserPublic, UsersPublic, UserUpdate

router = APIRouter()


@router.get("", response_model=UsersPublic)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """Get all users"""
    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)


@router.post("", response_model=UserPublic)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    user = get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = create_user(session=session, user_create=user_in)
    return user


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


@router.patch(
    "/{user_id}",
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: UUID,
    user_in: UserUpdate,
) -> Any:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    db_user = update_user(session=session, db_user=db_user, user_in=user_in)
    return db_user
