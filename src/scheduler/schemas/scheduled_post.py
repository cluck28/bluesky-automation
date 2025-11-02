from datetime import datetime

from pydantic import BaseModel


class ImageConfig(BaseModel):
    meta: dict


class ScheduledPost(BaseModel):
    path: str
    text: str
    date: datetime
    status: str
    image_config: ImageConfig
