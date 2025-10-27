from datetime import datetime

from pydantic import BaseModel


class Repost(BaseModel):
    post_uri: str
    post_indexed_at: datetime
    indexed_at: datetime
    handle: str
