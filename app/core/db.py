from core.config import settings
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    SQLModel.metadata.create_all(engine)
