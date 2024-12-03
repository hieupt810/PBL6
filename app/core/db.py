from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel, select

from app.core.config import settings
from app.models.constant import Constant
from app.models.product import Product

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

CATEGORIES = [
    "Beauty Products",
    "Books",
    "Electronics",
    "Fashion",
    "Fitness Equipment",
    "Furniture",
    "Home Appliances",
    "Kitchenware",
    "Musical Instruments",
    "Toys",
]

TIME_RANGES = ["1", "3", "7", "14", "30"]


def init_db(session: Session) -> None:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    for name in CATEGORIES:
        category = Constant(name=name, type=0)
        session.add(category)
        session.commit()

    for time_range in TIME_RANGES:
        time = Constant(name=time_range, type=1)
        session.add(time)
        session.commit()

    session.exec(select(Product)).first()
