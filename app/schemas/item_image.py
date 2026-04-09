from pydantic import BaseModel
from pydantic.config import ConfigDict


class ItemImageResponse(BaseModel):
    id: int
    image_path: str

    model_config = ConfigDict(from_attributes=True)
