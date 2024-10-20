import uuid
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default=uuid.uuid4(), primary_key=True)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(default=datetime.now(), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int
