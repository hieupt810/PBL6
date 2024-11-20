import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.api.main import api_router
from app.core.config import settings
from app.core.db import engine, init_db
from app.tasks.alibaba import crawl_alibaba

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        crawl_alibaba,
        "cron",
        hour=settings.CRON_HOUR,
        minute=settings.CRON_MINUTE,
        jitter=120,
        id="crawl_products",
    )
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown()
        logger.info("Scheduler shut down.")


app = FastAPI(title="PBL6 API", lifespan=lifespan)
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
