from fastapi import APIRouter

from app.models.filter import FilterListPublic, FilterPublic
from app.utils import CLASSES

router = APIRouter()


@router.get("")
async def read_constants():
    # Classes
    class_options = []
    for value in CLASSES:
        label = value.replace("_", " ").title()
        class_options.append({"value": value, "label": label})

    classes = FilterPublic(
        options=class_options, parameter="c", placeholder="Select a category"
    )

    # Time ranges
    time_range_options = [{"value": "1", "label": "Last 1 day"}]
    for value in ["7", "14", "21"]:
        label = f"Last {value} days"
        time_range_options.append({"value": value, "label": label})

    time_ranges = FilterPublic(
        options=time_range_options, parameter="t", placeholder="Select a time range"
    )

    return FilterListPublic(data=[classes, time_ranges], count=2)
