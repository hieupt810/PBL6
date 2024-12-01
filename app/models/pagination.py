from pydantic import BaseModel


class Pagination(BaseModel):
    total_records: int
    total_pages: int
    current: int
    next: int | None
    prev: int | None
