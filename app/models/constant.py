from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class ConstantPublic(SQLModel):
    id: UUID = Field(default_factory=lambda: uuid4(), primary_key=True, index=True)
    name: str = Field(nullable=False)


class Constant(ConstantPublic, table=True):
    __tablename__ = "constants"

    type: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)


class FilterPublic(SQLModel):
    options: list[ConstantPublic]
    param: str
    placeholder: str


class FilterListPublic(SQLModel):
    data: list[FilterPublic]
    number: int
