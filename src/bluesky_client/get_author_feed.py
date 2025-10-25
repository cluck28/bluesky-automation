from typing import List
from bluesky_client.schemas.post import Post, Author, BskyRecord, Embed
from atproto import Client


def parse_author(author) -> Author:
    return Author(
        handle=author.handle
    )


def parse_record(record) -> BskyRecord:
    return BskyRecord(
        text=record.text
    )


def parse_embed(embed) -> Embed:
    embed_type = embed.py_type
    # Can post multiple images
    if embed_type == 'app.bsky.embed.images#view':
        return Embed(
            resource=embed.images[0].fullsize,
            thumbnail=embed.images[0].thumb,
            embed_type='images',
        )
    elif embed_type == 'app.bsky.embed.video#view':
        return Embed(
            resource=embed.playlist,
            thumbnail=embed.thumbnail,
            embed_type='video',
        )
    else:
        return Embed(
            resource='',
            thumbnail='',
            embed_type='other',
        )


def get_author_feed(client: Client, client_did: str, limit: int=30) -> List[Post]:
    data = client.get_author_feed(
        actor=client_did,
        filter='posts_and_author_threads',
        limit=30,
    )
    cleaned_data = []
    for item in data.feed:
        reply = item.reply
        reason = item.reason

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
    next_page = data.cursor
    print(next_page)
    return cleaned_data