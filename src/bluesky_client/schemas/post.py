from datetime import datetime

from pydantic import BaseModel


class Author(BaseModel):
    handle: str


class BskyRecord(BaseModel):
    text: str
    tags: list


class Embed(BaseModel):
    resource: str
    thumbnail: str
    embed_type: str


class Post(BaseModel):
    author: Author
    indexed_at: datetime
    record: BskyRecord
    embed: Embed
    like_count: int
    quote_count: int
    reply_count: int
    repost_count: int
    bookmark_count: int
