from datetime import datetime, timedelta
from typing import Dict

import pandas as pd
import pytz
from pandas import DataFrame


def get_likes_df(likes: list, follows: list, followers: list) -> DataFrame:
    likes_df = pd.DataFrame([like.dict() for like in likes])
    follows_df = pd.DataFrame([follow.dict() for follow in follows])
    followers_df = pd.DataFrame([follower.dict() for follower in followers])
    merged = likes_df.merge(
        follows_df[["handle", "follow_index"]], on="handle", how="left"
    )
    merged["following"] = merged["follow_index"].notnull()
    merged = merged[
        ["post_uri", "post_indexed_at", "indexed_at", "handle", "following"]
    ]
    merged = merged.merge(
        followers_df[["handle", "follow_index"]], on="handle", how="left"
    )
    merged["follower"] = merged["follow_index"].notnull()
    merged["type"] = "like"
    return merged[
        [
            "post_uri",
            "post_indexed_at",
            "indexed_at",
            "handle",
            "following",
            "follower",
            "type",
        ]
    ]


def get_reposts_df(reposts: list, follows: list, followers: list) -> DataFrame:
    reposts_df = pd.DataFrame([repost.dict() for repost in reposts])
    follows_df = pd.DataFrame([follow.dict() for follow in follows])
    followers_df = pd.DataFrame([follower.dict() for follower in followers])
    merged = reposts_df.merge(
        follows_df[["handle", "follow_index"]], on="handle", how="left"
    )
    merged["following"] = merged["follow_index"].notnull()
    merged = merged[
        ["post_uri", "post_indexed_at", "indexed_at", "handle", "following"]
    ]
    merged = merged.merge(
        followers_df[["handle", "follow_index"]], on="handle", how="left"
    )
    merged["follower"] = merged["follow_index"].notnull()
    merged["type"] = "repost"
    return merged[
        [
            "post_uri",
            "post_indexed_at",
            "indexed_at",
            "handle",
            "following",
            "follower",
            "type",
        ]
    ]


def get_engagement_score(feed_df: DataFrame, followers: int, period: str) -> int:
    if period == "day":
        window = 1
    elif period == "week":
        window = 7
    elif period == "month":
        window = 30
    elif period == "quarter":
        window = 90
    elif period == "year":
        window = 365
    else:
        window = 30
    df = feed_df.copy()
    df["indexed_at"] = pd.to_datetime(df["indexed_at"], utc=True)
    cutoff = datetime.now(pytz.UTC) - timedelta(days=window)
    filtered_df = df[df["indexed_at"] >= cutoff]
    print(filtered_df)
    return round((filtered_df["like_count"].sum() / followers) * 100, 0)


def get_engagement_df(
    feed_posts: Dict, likes_df: DataFrame, reposts_df: DataFrame, user_handle: str
) -> DataFrame:
    post_list = []
    for item in feed_posts:
        if item.author.handle != user_handle:
            continue
        post_list.append(
            {
                "post_uri": item.uri,
                "post_indexed_at": item.indexed_at,
                "indexed_at": item.indexed_at,
                "handle": user_handle,
                "following": False,
                "follower": False,
                "type": "post",
            }
        )
    feed_df = pd.DataFrame(post_list)
    return pd.concat([likes_df, reposts_df, feed_df], ignore_index=True)
