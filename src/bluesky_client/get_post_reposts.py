import time
from typing import List

from atproto import Client
from pydantic import ValidationError

from bluesky_client.schemas.repost import Repost


def get_post_reposts(
    client: Client, user_feed: list, user_handle: str, limit: int = 100
) -> List[Repost]:
    cleaned_data = []
    for item in user_feed:
        if item.author.handle != user_handle:
            continue
        cursor = None
        while True:
            data = client.get_reposted_by(
                uri=item.uri,
                limit=limit,
                cursor=cursor,
            )
            if not data.reposted_by:
                break
            for repost in data.reposted_by:
                try:
                    parsed_repost = Repost(
                        post_uri=item.uri,
                        post_indexed_at=item.indexed_at,
                        indexed_at=repost.indexed_at,
                        handle=repost.handle,
                    )
                    cleaned_data.append(parsed_repost)
                except ValidationError:
                    pass
            cursor = data.cursor
            if not cursor:
                break
    return cleaned_data
