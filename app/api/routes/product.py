from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from uuid import UUID

from fastapi import APIRouter
from sqlalchemy import func
from sqlmodel import select

from app.api.deps import SessionDep
from app.logger import get_logger
from app.models.constant import Constant
from app.models.pagination import Pagination
from app.models.product import Product, ProductListPublic

logger = get_logger(__name__)
router = APIRouter()


def get_constant_by_type(session: SessionDep, type: int):
    stmt = (
        select(Constant)
        .where(Constant.type == type)
        .order_by(Constant.created_at)
        .limit(1)
    )
    result = session.exec(stmt).first()
    return result


@router.get("", response_model=ProductListPublic)
async def read_products_list(
    session: SessionDep,
    category: str = None,
    time: str = None,
    page: int = 1,
    size: int = 10,
) -> ProductListPublic:
    days = 1
    if not time:
        obj = get_constant_by_type(session, 1)

        time = obj.id
        days = int(obj.name)

    page = 1 if page < 1 else page
    size = 10 if size < 1 else size
    date = datetime.combine(
        datetime.now(timezone.utc) - timedelta(days=days), datetime.min.time()
    )

    # Get products
    stmt = (
        select(Product)
        .where(Product.updated_at >= date)
        .order_by(Product.updated_at.desc())
        .limit(size)
        .offset((page - 1) * size)
    )
    result = session.exec(stmt).all()

    # Pagination
    stmt = select(func.count()).select_from(Product).where(Product.updated_at >= date)
    total_records = session.exec(stmt).one()
    total_pages = (total_records + size - 1) // size
    pagination = Pagination(
        total_records=total_records,
        total_pages=total_pages,
        current=page,
        next=page + 1 if page < total_pages else None,
        prev=page - 1 if page > 1 else None,
    )

    return ProductListPublic(data=result, pagination=pagination)

@router.get("/{product_id}", response_model=Product)
async def read_product_detail(product_id: UUID, session: SessionDep) -> Product:
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
