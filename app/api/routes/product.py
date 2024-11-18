import logging

from fastapi import APIRouter
from pydantic import ValidationError
from sqlalchemy import func
from sqlmodel import select

from app.api.deps import SessionDep
from app.models.pagination import Pagination
from app.models.product import Product, ProductsPublic

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("", response_model=ProductsPublic)
async def read_products_list(
    session: SessionDep, page: int = 1, size: int = 10
) -> ProductsPublic:
    _page = max(1, page)
    _size = size if size > 0 else 10

    # Count the total number of products
    count_stmt = select(func.count()).select_from(Product)
    count = session.exec(count_stmt).one()

    # Get the products for the current page
    stmt = (
        select(Product)
        .order_by(Product.created_at.desc())
        .offset((_page - 1) * _size)
        .limit(_size)
    )
    products = session.exec(stmt).all()

    # Create a pagination object
    total_pages = count // _size + 1 if count % _size else count // _size
    try:
        pagination = Pagination(
            total_records=count,
            current_page=_page,
            total_pages=total_pages,
            next_page=_page + 1 if _page < total_pages else None,
            previous_page=_page - 1 if _page > 1 else None,
        )
    except ValidationError as e:
        raise e

    return ProductsPublic(data=products, pagination=pagination)
