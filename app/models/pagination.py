from sqlmodel import SQLModel


class Pagination(SQLModel):
    total: int
    next: int | None
    current: int | None
    previous: int | None
