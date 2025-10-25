from typing import Dict

import pandas as pd
from pandas import DataFrame


# Function to create the dataframe
def get_user_feed_df(user_feed: list) -> DataFrame:
    data = []
    for post in user_feed:
        ts = post.indexed_at
        likes = post.like_count
        handle = post.author.handle
        if handle == "pupbiscuit24.bsky.social":
            data.append({"indexed_at": ts, "like_count": likes})
    return pd.DataFrame(data)


def likes_by_month(feed_df: DataFrame) -> Dict:
    df = feed_df
    df["indexed_at"] = pd.to_datetime(df["indexed_at"])
    df["month"] = df["indexed_at"].dt.to_period("M")
    # Aggregate — for example, sum of values per month
    agg_df = df.groupby("month", as_index=False).agg(
        total_likes=("like_count", "sum"),
        avg_likes=("like_count", "mean"),
        total_posts=("like_count", "count"),
    )
    agg_df["month"] = agg_df["month"].astype(str)
    return (
        {"labels": agg_df.month.to_list(), "values": agg_df.total_likes.to_list()},
        {"labels": agg_df.month.to_list(), "values": agg_df.avg_likes.to_list()},
        {"labels": agg_df.month.to_list(), "values": agg_df.total_posts.to_list()},
    )
