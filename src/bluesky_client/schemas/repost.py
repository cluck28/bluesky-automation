from datetime import datetime

from pydantic import BaseModel

from typing import Optional


class Repost(BaseModel):
    post_uri: str
    post_indexed_at: datetime
    indexed_at: datetime
    handle: str
    avatar: Optional[str] = None
