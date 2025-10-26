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
            data.append(
                {
                    "indexed_at": ts,
                    "like_count": likes,
                    "reply_count": replies,
                    "quote_count": quotes,
                    "repost_count": reposts,
                    "bookmark_count": bookmarks,
                }
            )
    return pd.DataFrame(data)


def agg_user_feed_dataframe(
    feed_df: DataFrame, agg_column: str, column: str, agg: str, period: str
) -> Dict:
    df = feed_df
    df["indexed_at"] = pd.to_datetime(df["indexed_at"])
    if period == "day":
        df["cohort"] = df["indexed_at"].dt.to_period("D")
    elif period == "week":
        df["cohort"] = df["indexed_at"].dt.to_period("W")
    elif period == "month":
        df["cohort"] = df["indexed_at"].dt.to_period("M")
    elif period == "quarter":
        df["cohort"] = df["indexed_at"].dt.to_period("Q")
    elif period == "year":
        df["cohort"] = df["indexed_at"].dt.to_period("Y")
    else:
        df["cohort"] = df["indexed_at"].dt.to_period("M")
    # Aggregate — for example, sum of values per month
    agg_df = df.groupby("cohort", as_index=False).agg(
        agg_column=(column, agg),
    )
    agg_df["cohort"] = agg_df["cohort"].astype(str)
    agg_df[agg_column] = agg_df["agg_column"]
    return {
        "labels": agg_df["cohort"].to_list(),
        "values": agg_df[agg_column].to_list(),
    }


def stacked_agg_user_feed_dataframe(feed_df: DataFrame, agg: str, period: str) -> Dict:
    data_types = [
        "like_count",
        "reply_count",
        "quote_count",
        "bookmark_count",
        "repost_count",
    ]
    df = feed_df
    df["indexed_at"] = pd.to_datetime(df["indexed_at"])
    if period == "day":
        df["cohort"] = df["indexed_at"].dt.to_period("D")
    elif period == "week":
        df["cohort"] = df["indexed_at"].dt.to_period("W")
    elif period == "month":
        df["cohort"] = df["indexed_at"].dt.to_period("M")
    elif period == "quarter":
        df["cohort"] = df["indexed_at"].dt.to_period("Q")
    elif period == "year":
        df["cohort"] = df["indexed_at"].dt.to_period("Y")
    else:
        df["cohort"] = df["indexed_at"].dt.to_period("M")
    # Aggregate — for example, sum of values per month
    if agg == "sum":
        agg_df = df.groupby("cohort", as_index=False)[data_types].sum()
    elif agg == "mean":
        agg_df = df.groupby("cohort", as_index=False)[data_types].mean()
    else:
        agg_df = df.groupby("cohort", as_index=False)[data_types].sum()
    agg_df["cohort"] = agg_df["cohort"].astype(str)
    return {
        "labels": agg_df["cohort"].to_list(),
        "datasets": [
            {
                "label": "Likes",
                "data": agg_df["like_count"].to_list(),
                "backgroundColor": "rgba(255, 99, 132, 0.6)",
            },
            {
                "label": "Replies",
                "data": agg_df["reply_count"].to_list(),
                "backgroundColor": "rgba(54, 162, 235, 0.6)",
            },
            {
                "label": "Reposts",
                "data": agg_df["repost_count"].to_list(),
                "backgroundColor": "rgba(255, 206, 86, 0.6)",
            },
            {
                "label": "Quotes",
                "data": agg_df["quote_count"].to_list(),
                "backgroundColor": "rgba(153, 102, 255, 0.6)",
            },
            {
                "label": "Bookmarks",
                "data": agg_df["bookmark_count"].to_list(),
                "backgroundColor": "rgba(75, 192, 192, 0.6)",
            },
        ],
    }
