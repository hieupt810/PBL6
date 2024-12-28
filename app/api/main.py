from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.routes.filter import router as filter_router
from app.api.routes.product import router as product_router
from app.utils import predict, save_image

api_router = APIRouter()
api_router.include_router(product_router, prefix="/product", tags=["Product"])
api_router.include_router(filter_router, prefix="/const", tags=["Constant"])


class TestModel(BaseModel):
    image_url: str
    model: Literal["resnet", "vit", "resnet_self"]


@api_router.post("/test")
async def test_model(body: TestModel):
    filename = save_image(body.image_url)
    category, probs = predict(filename, model_type=body.model)

    return {"category": category, "probabilities": f"{probs}%"}
