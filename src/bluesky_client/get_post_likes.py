import time
from typing import List

from atproto import Client

from bluesky_client.schemas.like import Like


def get_post_likes(
    client: Client, user_feed: list, user_handle: str, limit: int = 100
) -> List[Like]:
    cleaned_data = []
    for item in user_feed:
        if item.author.handle != user_handle:
            continue
        cursor = None
        while True:
            data = client.get_likes(
                uri=item.uri,
                limit=limit,
                cursor=cursor,
            )
            if not data.likes:
                break
            for like in data.likes:
                parsed_like = Like(
                    post_uri=item.uri,
                    post_indexed_at=item.indexed_at,
                    indexed_at=like.indexed_at,
                    handle=like.actor.handle,
                )
                cleaned_data.append(parsed_like)
            cursor = data.cursor
            if not cursor:
                break
    return cleaned_data
