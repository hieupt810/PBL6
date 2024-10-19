import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    title: str = Field(index=True, max_length=1000)
    image: str = Field(max_length=1000, nullable=True)
    href: str = Field(max_length=1000, nullable=True)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class Product(ProductBase, table=True):
    id: uuid.UUID = Field(default=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default=lambda: datetime.now(), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)


class ProductPublic(ProductBase):
    id: uuid.UUID


class ProductsPublic(SQLModel):
    data: list[ProductPublic]
    count: int
