from datetime import datetime

from pydantic import BaseModel


class ScheduledPost(BaseModel):
    path: str
    text: str
    date: datetime
    status: str
