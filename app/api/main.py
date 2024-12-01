from fastapi import APIRouter

from app.api.routes.constant import router as constant_router
from app.api.routes.product import router as product_router

api_router = APIRouter()
api_router.include_router(product_router, prefix="/product", tags=["Product"])
api_router.include_router(constant_router, prefix="/const", tags=["Constant"])
