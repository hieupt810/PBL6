import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.api.routes.filter import router as filter_router
from app.api.routes.product import router as product_router

api_router = APIRouter()
api_router.include_router(product_router, prefix="/product", tags=["Product"])
api_router.include_router(filter_router, prefix="/const", tags=["Constant"])


@api_router.get("/image/{filename}")
async def get_image(filename: str):
    image_path = os.path.join(os.getcwd(), "images", filename)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(image_path)
