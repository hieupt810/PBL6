from sqlmodel import SQLModel


class FilterPublic(SQLModel):
    options: list
    parameter: str
    placeholder: str


class FilterListPublic(SQLModel):
    data: list[FilterPublic]
    count: int
