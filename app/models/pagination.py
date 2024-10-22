from sqlmodel import SQLModel


class Pagination(SQLModel):
    total_records: int
    current_page: int
    total_pages: int
    next_page: int | None
    previous_page: int | None
