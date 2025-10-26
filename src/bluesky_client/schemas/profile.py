from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Profile(BaseModel):
    did: str
    handle: str
    followers_count: int
    follows_count: int
    created_at: datetime


class Follower(BaseModel):
    did: str
    handle: str
    display_name: Optional[str] = None
    indexed_at: Optional[datetime] = None
    created_at: datetime
    follow_index: int
