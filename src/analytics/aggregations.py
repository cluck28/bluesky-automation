from typing import Dict

import pandas as pd
from pandas import DataFrame


# Function to create the dataframe
def get_user_feed_df(user_feed: list, user_handle: str) -> DataFrame:
    data = []
    for post in user_feed:
        ts = post.indexed_at
        likes = post.like_count
        reposts = post.repost_count
        replies = post.reply_count
        quotes = post.quote_count
        bookmarks = post.bookmark_count
        handle = post.author.handle
        if handle == user_handle:
            data.append({
                "indexed_at": ts,
                "like_count": likes,
                "reply_count": replies,
                "quote_count": quotes,
                "repost_count": reposts,
                "bookmark_count": bookmarks,
            })
    return pd.DataFrame(data)


def agg_user_feed_dataframe(feed_df: DataFrame, agg_column: str, column: str, agg: str, period: str) -> Dict:
    df = feed_df
    df["indexed_at"] = pd.to_datetime(df["indexed_at"])
    df["month"] = df["indexed_at"].dt.to_period("M")
    # Aggregate — for example, sum of values per month
    agg_df = df.groupby("month", as_index=False).agg(
        agg_column=(column, agg),
    )
    agg_df["month"] = agg_df["month"].astype(str)
    agg_df[agg_column] = agg_df["agg_column"]
    return {"labels": agg_df["month"].to_list(), "values": agg_df[agg_column].to_list()}
