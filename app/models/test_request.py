from pydantic import BaseModel


class TestModel(BaseModel):
    image_url: str
    model: str
