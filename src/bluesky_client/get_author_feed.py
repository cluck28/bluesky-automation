import re
from typing import List

from atproto import Client

from bluesky_client.schemas.post import Author, BskyRecord, Embed, Post


def find_tags(text: str) -> List[str]:
    pattern = r"#[A-Za-z0-9_]+"
    return [tag[1:] for tag in re.findall(pattern, text)]


def parse_author(author) -> Author:
    return Author(handle=author.handle)


def parse_record(record) -> BskyRecord:
    return BskyRecord(
        text=record.text,
        tags=find_tags(record.text),
    )


def parse_embed(embed) -> Embed:
    try:
        embed_type = embed.py_type
        # Can post multiple images
        if embed_type == "app.bsky.embed.images#view":
            return Embed(
                resource=embed.images[0].fullsize,
                thumbnail=embed.images[0].thumb,
                embed_type="images",
            )
        elif embed_type == "app.bsky.embed.video#view":
            return Embed(
                resource=embed.playlist,
                thumbnail=embed.thumbnail,
                embed_type="video",
            )
        else:
            return Embed(
                resource="",
                thumbnail="",
                embed_type="other",
            )
    except AttributeError:
        return Embed(
            resource="",
            thumbnail="",
            embed_type="other",
        )


def get_author_feed(client: Client, client_did: str, limit: int = 30) -> List[Post]:
    cursor = None
    cleaned_data = []
    while True:
        data = client.get_author_feed(
            actor=client_did,
            filter="posts_and_author_threads",
            limit=50,
            cursor=cursor,
        )
        if not data.feed:
            break
        for item in data.feed:
            # reply = item.reply
            # reason = item.reason

            post = item.post
            parsed_post = Post(
                author=parse_author(post.author),
                indexed_at=post.indexed_at,
                record=parse_record(post.record),
                embed=parse_embed(post.embed),
                like_count=post.like_count,
                quote_count=post.quote_count,
                reply_count=post.reply_count,
                repost_count=post.repost_count,
                bookmark_count=post.bookmarkCount,
            )
            cleaned_data.append(parsed_post)
        cursor = data.cursor
        if not cursor:
            break
    return cleaned_data
