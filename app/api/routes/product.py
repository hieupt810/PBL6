from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from sqlalchemy import func
from sqlmodel import select

from app.api.deps import SessionDep
from app.models.pagination import Pagination
from app.models.product import Product, ProductsResponse

router = APIRouter()


@router.get("", response_model=ProductsResponse)
async def read_products_list(
    session: SessionDep,
    c: str = None,
    t: str = "30",
    page: int = 1,
    size: int = 10,
) -> ProductsResponse:
    # Format datetime
    from_date = datetime.combine(
        datetime.now(timezone.utc) - timedelta(days=int(t)), datetime.min.time()
    )

    # Pagnination
    stmt = (
        select(func.count()).select_from(Product).where(Product.created_at >= from_date)
    )
    total_records = session.exec(stmt).one()
    total_pages = (total_records + size - 1) // size

    if page < 1 or (page > total_pages and page != 1) or size < 1:
        raise HTTPException(status_code=400, detail="Invalid pagination parameters")

    # Products
    stmt = select(Product).where(Product.created_at >= from_date)
    if c:
        stmt = stmt.where(Product.category == c.lower())

    stmt = (
        stmt.order_by(Product.created_at.desc()).limit(size).offset((page - 1) * size)
    )
    products = session.exec(stmt).all()

    return ProductsResponse(
        data=products,
        pagination=Pagination(
            total=total_pages,
            current=page,
            next=page + 1 if page < total_pages else None,
            previous=page - 1 if page > 1 else None,
        ),
    )


@router.get("/{id}", response_model=Product)
async def read_product_detail(id: str, session: SessionDep) -> Product:
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product
