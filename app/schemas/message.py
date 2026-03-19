from pydantic import BaseModel
from pydantic.config import ConfigDict

from app.schemas.user import PublicUsersResponse


class MessageResponse(BaseModel):
    sender: PublicUsersResponse
    receiver: PublicUsersResponse
    message: str

    model_config = ConfigDict(from_attributes=True)
