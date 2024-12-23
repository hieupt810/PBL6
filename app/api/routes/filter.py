from fastapi import APIRouter

from app.models.filter import FilterListPublic, FilterPublic
from app.utils import CLASSES

router = APIRouter()


@router.get("")
async def read_constants():
    classes = FilterPublic(
        options=CLASSES, parameter="c", placeholder="Select a category"
    )
    time_ranges = FilterPublic(
        options=["1", "7", "14", "21"],
        parameter="t",
        placeholder="Select a time range",
    )

    return FilterListPublic(data=[classes, time_ranges], count=2)
