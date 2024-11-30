from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.models.pagination import Pagination


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: UUID = Field(default_factory=lambda: uuid4(), primary_key=True, index=True)
    title: str = Field()
    price: str = Field(nullable=False)
    image_url: str | None = Field(default=None, nullable=True)
    url: str = Field(nullable=False)

    category_id: UUID | None = Field(foreign_key="constants.id")

    created_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)


class ProductsPublic(SQLModel):
    data: list[Product]
    pagination: Pagination
