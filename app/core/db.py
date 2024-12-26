from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel, select

from app.core.config import settings
from app.main import crawl_function
from app.models.product import Product

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    session.exec(select(Product)).first()

    crawl_function()
