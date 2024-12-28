from pydantic import BaseModel


class Pagination(BaseModel):
    total: int
    next: int | None
    current: int | None
    previous: int | None
