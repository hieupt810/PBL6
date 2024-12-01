from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.core.db import engine
from app.logger import get_logger
from app.models.product import Product

logger = get_logger(__name__)


def product_cleaner():
    with Session(engine) as session:
        thirty_days_ago = datetime.combine(
            datetime.now(timezone.utc) - timedelta(days=30), datetime.min.time()
        )
        products = session.exec(
            select(Product).filter(Product.created_at < thirty_days_ago)
        )
        for product in products:
            try:
                session.delete(product)
                session.commit()
            except Exception:
                logger.error(f"Error while deleting product {product.id}")
