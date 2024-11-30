from fastapi import APIRouter
from sqlmodel import select

from app.api.deps import SessionDep
from app.logger import get_logger
from app.models.constant import Constant, FilterPublic

router = APIRouter()

logger = get_logger(__name__)


@router.get("", response_model=FilterPublic)
async def read_filter_list(session: SessionDep) -> FilterPublic:
    category_stmt = select(Constant).where(Constant.type == 0).order_by(Constant.name)
    categories = session.exec(category_stmt).all()

    time_stmt = select(Constant).where(Constant.type == 1).order_by(Constant.created_at)
    time = session.exec(time_stmt).all()

    return FilterPublic(categories=categories, time=time)
