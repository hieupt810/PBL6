from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

from app.core.config import settings
from app.models import *

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    SQLModel.metadata.create_all(engine)
