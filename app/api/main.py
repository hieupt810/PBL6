from fastapi import APIRouter, HTTPException

from app.api.routes.product import router as product_router
from app.models.filter import FilterListPublic, FilterPublic
from app.models.test_request import TestModel
from app.utils import CLASSES, predict, save_image

api_router = APIRouter()
api_router.include_router(product_router, prefix="/product", tags=["Product"])


@api_router.get("/const")
async def read_constants():
    data = []

    # Page size
    size_options = []
    for value in sorted([8, 16, 32, 64]):
        size_options.append({"value": f"{value}", "label": f"{value}"})

    data.append(
        FilterPublic(
            options=size_options, parameter="size", placeholder="Number of shown items"
        )
    )

    # Categories
    class_options = [{"value": "", "label": "All categories"}]
    for value in sorted(CLASSES):
        label = value.replace("_", " ").title()
        class_options.append({"value": value, "label": label})

    data.append(
        FilterPublic(options=class_options, parameter="c", placeholder="Category")
    )

    # Time ranges
    time_range_options = []
    for value in sorted([7, 14, 21, 30], reverse=True):
        label = f"Last {value} days"
        time_range_options.append({"value": f"{value}", "label": label})

    data.append(
        FilterPublic(
            options=time_range_options, parameter="t", placeholder="Time range"
        )
    )

    # Sort options
    sort_options = [
        {"value": "1", "label": "Newest"},
        {"value": "2", "label": "Price: Low to High"},
        {"value": "3", "label": "Price: High to Low"},
        {"value": "4", "label": "Probability"},
    ]
    data.append(
        FilterPublic(options=sort_options, parameter="sort", placeholder="Sort")
    )

    return FilterListPublic(data=data, count=len(data))


@api_router.post("/test")
async def test_model(body: TestModel):
    filename = save_image(body.image_url)
    if body.model not in ["resnet", "vit", "resnet_self"]:
        raise HTTPException(status_code=400, detail="Invalid model type.")

    category, probs = predict(filename, model_type=body.model)
    return {"category": category, "probabilities": f"{probs}%"}
