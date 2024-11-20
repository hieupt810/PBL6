import logging
from datetime import datetime, timezone

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
    page = max(1, page)
    if size < 1:
        size = 10

    # Count the total number of products
    count_stmt = select(func.count()).select_from(Product)
    count = session.exec(count_stmt).one()

    today = datetime.now(timezone.utc).date()
    start_of_today = datetime.combine(today, datetime.min.time())
    end_of_today = datetime.combine(today, datetime.max.time())

    # Get the products for the current page
    stmt = (
        select(Product)
        .where(Product.created_at.between(start_of_today, end_of_today))
        .order_by(Product.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    products = session.exec(stmt).all()

    # Create a pagination object
    total_pages = count // size + 1 if count % size else count // size
    try:
        pagination = Pagination(
            total_records=count,
            current_page=page,
            total_pages=total_pages,
            next_page=page + 1 if page < total_pages else None,
            previous_page=page - 1 if page > 1 else None,
        )
    except ValidationError as e:
        raise e

    return ProductsPublic(data=products, pagination=pagination)
