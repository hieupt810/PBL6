from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel, select

from app.core.config import settings
from app.helpers.user import create_user
from app.models import *
from app.models.user import User, UserCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.SUPERUSER_EMAIL)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.SUPERUSER_EMAIL, password=settings.SUPERUSER_PASSWORD
        )
        user = create_user(session=session, user_create=user_in)
