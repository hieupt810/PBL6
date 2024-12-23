from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.core.db import engine
from app.models.product import Product


def cleaner():
    thirty_days_ago = datetime.combine(
        datetime.now(timezone.utc) - timedelta(days=30), datetime.min.time()
    )

    with Session(engine) as session:
        products = session.exec(
            select(Product).filter(Product.created_at < thirty_days_ago)
        )

        for product in products:
            try:
                session.delete(product)
                session.commit()
            except Exception:
                print("Failed to delete product with id", product)
