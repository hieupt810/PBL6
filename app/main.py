from api.main import api_router
from core.config import settings
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(title="PBL6 API")

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
