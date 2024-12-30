from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.pagination import Pagination
from app.utils import generate_id


class ProductPublic(SQLModel):
    id: str = Field(default_factory=lambda: generate_id(), primary_key=True, index=True)

    category: str | None = Field(nullable=False)
    probability: str | None = Field(nullable=False)
    image: str | None = Field(default=None, nullable=True)

    name: str = Field(nullable=False)
    price: str = Field(nullable=False)
    base_url: str = Field(nullable=False)
    description: str = Field(nullable=False)


class Product(ProductPublic, table=True):
    __tablename__ = "products"

    created_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)

    def __repr__(self):
        return f"<Product id='{self.id}'>"


class ProductsResponse(SQLModel):
    data: list[Product]
    pagination: Pagination
