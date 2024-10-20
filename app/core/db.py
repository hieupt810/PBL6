from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel, select

from app.core.config import settings
from app.models.product import Product

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    SQLModel.metadata.create_all(engine)

    session.exec(select(Product)).first()
