from pydantic import BaseModel, model_validator
from typing_extensions import Self


class Pagination(BaseModel):
    total_records: int
    current_page: int
    total_pages: int
    next_page: int | None
    previous_page: int | None
