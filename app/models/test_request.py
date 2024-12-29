from typing import Literal

from pydantic import BaseModel


class TestModel(BaseModel):
    image_url: str
    model: Literal["resnet", "vit", "resnet_self"]
