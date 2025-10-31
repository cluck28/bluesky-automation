from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Repost(BaseModel):
    post_uri: str
    post_indexed_at: datetime
    indexed_at: datetime
    handle: str
    avatar: Optional[str] = None
