from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.models.pagination import Pagination


class ProductPublic(SQLModel):
    id: UUID = Field(default_factory=lambda: uuid4(), primary_key=True, index=True)
    category: UUID | None = Field(foreign_key="constants.id")

    name: str = Field(nullable=False)
    price: str = Field(nullable=False)
    image: str | None = Field(default=None, nullable=True)
    base: str = Field(nullable=False)


class Product(ProductPublic, table=True):
    __tablename__ = "products"

    created_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)


class ProductListPublic(SQLModel):
    data: list[Product]
    pagination: Pagination
