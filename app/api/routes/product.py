from fastapi import APIRouter
from sqlalchemy import func
from sqlmodel import select

from app.api.deps import SessionDep
from app.models.product import Product, ProductsPublic

router = APIRouter()


@router.get("", response_model=ProductsPublic)
async def read_products_list(
    session: SessionDep, page: int = 1, per_page: int = 10
) -> ProductsPublic:
    _page = max(1, page)
    _per_page = per_page if per_page > 0 else 10

    count_statement = select(func.count()).select_from(Product)
    count = session.exec(count_statement).one()

    statement = select(Product).offset(_page * _per_page).limit(_per_page)
    products = session.exec(statement).all()

    return ProductsPublic(data=products, count=count)
