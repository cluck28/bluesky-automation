from datetime import datetime, timedelta

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
    return merged[
        ["post_uri", "post_indexed_at", "indexed_at", "handle", "following", "follower"]
    ]


def get_engagement_score(likes_df: DataFrame, followers: int) -> int:
    likes_df["indexed_at"] = pd.to_datetime(likes_df["indexed_at"], utc=True)
    cutoff = datetime.now(pytz.UTC) - timedelta(days=90)
    filtered_df = likes_df[likes_df["indexed_at"] >= cutoff]
    return round(
        (filtered_df[filtered_df["follower"]]["handle"].nunique() / followers) * 100, 0
    )
