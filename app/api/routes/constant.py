from fastapi import APIRouter
from sqlmodel import select

from app.api.deps import SessionDep
from app.logger import get_logger
from app.models.constant import Constant, FilterListPublic, FilterPublic

logger = get_logger(__name__)
router = APIRouter()


@router.get("", response_model=FilterListPublic)
async def read_filter_list(session: SessionDep) -> FilterListPublic:
    # Get all categories
    stmt = select(Constant).where(Constant.type == 0).order_by(Constant.name)
    result = session.exec(stmt).all()
    category_options = FilterPublic(
        options=result, param="c", placeholder="Select a category"
    )

    # Get all times
    stmt = select(Constant).where(Constant.type == 1).order_by(Constant.created_at)
    result = session.exec(stmt).all()
    for time in result:
        if time.name == "1":
            time.name = "Last 1 day"
        else:
            time.name = f"Last {time.name} days"

    time_options = FilterPublic(options=result, param="t", placeholder="Select a time")

    return FilterListPublic(data=[category_options, time_options], number=2)
