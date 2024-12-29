from fastapi import APIRouter

from app.api.routes.product import router as product_router
from app.models.filter import FilterListPublic, FilterPublic
from app.models.test_request import TestModel
from app.utils import CLASSES, predict, save_image

api_router = APIRouter()
api_router.include_router(product_router, prefix="/product", tags=["Product"])


@api_router.get("/const")
async def read_constants():
    class_options = []
    for value in CLASSES:
        label = value.replace("_", " ").title()
        class_options.append({"value": value, "label": label})

    classes = FilterPublic(
        options=class_options, parameter="c", placeholder="Select a category"
    )

    time_range_options = [{"value": "1", "label": "Last 1 day"}]
    for value in ["7", "14", "21"]:
        label = f"Last {value} days"
        time_range_options.append({"value": value, "label": label})

    time_ranges = FilterPublic(
        options=time_range_options, parameter="t", placeholder="Select a time range"
    )

    return FilterListPublic(data=[classes, time_ranges], count=2)


@api_router.post("/test")
async def test_model(body: TestModel):
    filename = save_image(body.image_url)
    category, probs = predict(filename, model_type=body.model)

    return {"category": category, "probabilities": f"{probs}%"}
