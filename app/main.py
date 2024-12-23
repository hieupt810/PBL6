from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.api.main import api_router
from app.core.config import settings
from app.core.db import engine, init_db
from app.tasks.alibaba import alibaba
from app.tasks.cleaner import cleaner


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        alibaba,
        "cron",
        hour=settings.CRON_HOUR,
        minute=settings.CRON_MINUTE,
        id="alibaba",
    )
    scheduler.add_job(
        cleaner, "cron", day_of_week="mon", hour=0, minute=0, id="cleaner"
    )

    try:
        scheduler.start()
        print("All jobs scheduled.")
        yield
    finally:
        scheduler.shutdown()
        print("All jobs stopped.")


app = FastAPI(title="PBL6 FastAPI", lifespan=lifespan)
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
