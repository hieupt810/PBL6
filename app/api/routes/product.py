import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy import func
from sqlmodel import select

from app.api.deps import SessionDep
from app.core.crawler import Driver
from app.models.message import Message
from app.models.pagination import Pagination
from app.models.product import Product, ProductsPublic
from app.utils import load_json

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
    pagination = Pagination(
        total_records=count,
        current_page=_page,
        total_pages=total_pages,
        next_page=_page + 1 if _page < total_pages else None,
        previous_page=_page - 1 if _page > 1 else None,
    )

    return ProductsPublic(data=products, pagination=pagination)


@router.post("", response_model=Message)
async def crawl_product(session: SessionDep) -> Message:
    driver = Driver()
    try:
        data = load_json("alibaba")
        for link in data["categories"]:
            driver.get(link)

            titles = driver.find_by_css_selector(data["title"])
            images = driver.find_by_css_selector(data["image"])
            hrefs = driver.find_by_css_selector(data["href"])
            prices = driver.find_by_css_selector(data["price"])

            if not (len(titles) == len(images) == len(prices) == len(hrefs)):
                raise HTTPException(status_code=400, detail="Invalid data")

            logger.info(f"Found {len(titles)} products in {link}")
            for title, image, price, href in zip(titles, images, prices, hrefs):
                product = Product(
                    title=title.text,
                    image_href=image.get_attribute("src"),
                    shopping_href=href.get_attribute("href"),
                    price=price.text,
                )
                session.add(product)
                session.commit()

            logger.info(f"Successfully updated to the database!")
    finally:
        driver.close()

    return Message(message="Products have been crawled successfully")
