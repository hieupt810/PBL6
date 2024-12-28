from pydantic import BaseModel


class FilterPublic(BaseModel):
    options: list
    parameter: str
    placeholder: str


class FilterListPublic(BaseModel):
    data: list[FilterPublic]
    count: int
