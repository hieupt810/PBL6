from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Product(SQLModel, table=True):
    id: UUID = Field(default=uuid4(), primary_key=True, index=True)

    title: str = Field()
    image_href: str | None = Field(default=None, nullable=True)
    shopping_href: str = Field(nullable=False)

    created_at: datetime = Field(default=datetime.now(), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)


class ProductsPublic(SQLModel):
    data: list[Product]
    count: int
