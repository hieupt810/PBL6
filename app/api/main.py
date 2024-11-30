from fastapi import APIRouter

from app.api.routes.library import router as library_router
from app.api.routes.product import router as product_router

api_router = APIRouter()
api_router.include_router(product_router, prefix="/product", tags=["Product"])
api_router.include_router(library_router, prefix="/const", tags=["Constant"])
