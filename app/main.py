from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.api.main import api_router
from app.core.config import settings
from app.core.db import engine, init_db

app = FastAPI(title="PBL6 API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=(
        settings.all_cors_origins if settings.all_cors_origins else ["localhost"]
    ),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


def init() -> None:
    with Session(engine) as session:
        init_db(session)


if settings.POSTGRES_RESET_TABLES:
    init()

app.include_router(api_router, prefix=settings.API_V1_STR)
