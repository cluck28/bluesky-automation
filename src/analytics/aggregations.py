from typing import Dict

import pandas as pd
from pandas import DataFrame


# Function to create the dataframe
def get_user_feed_df(user_feed: list, user_handle: str) -> DataFrame:
    data = []
    for post in user_feed:
        ts = post.indexed_at
        embed_type = post.embed.embed_type
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
                    "embed_type": embed_type,
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


def embed_type_agg_user_feed_dataframe(
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
    agg_df = df.groupby(["cohort", "embed_type"], as_index=False).agg(
        agg_column=(column, agg),
    )
    agg_df["cohort"] = agg_df["cohort"].astype(str)
    agg_df[agg_column] = agg_df["agg_column"]
    # We need to infill values where we are missing date <> embed_type combos
    all_periods = agg_df["cohort"].unique()
    all_types = agg_df["embed_type"].unique()
    full_index = pd.MultiIndex.from_product(
        [all_periods, all_types], names=["cohort", "embed_type"]
    )
    df_full = (
        agg_df.set_index(["cohort", "embed_type"])
        .reindex(full_index, fill_value=0)
        .reset_index()
    )
    return {
        "labels": df_full[df_full["embed_type"] == "images"]["cohort"].to_list(),
        "datasets": [
            {
                "label": "Images",
                "data": df_full[df_full["embed_type"] == "images"][
                    agg_column
                ].to_list(),
                "backgroundColor": "rgba(255, 99, 132, 0.6)",
            },
            {
                "label": "Video",
                "data": df_full[df_full["embed_type"] == "video"][agg_column].to_list(),
                "backgroundColor": "rgba(54, 162, 235, 0.6)",
            },
            {
                "label": "Other",
                "data": df_full[df_full["embed_type"] == "other"][agg_column].to_list(),
                "backgroundColor": "rgba(255, 206, 86, 0.6)",
            },
        ],
    }


def agg_engagement_rate(engagement_df: DataFrame) -> Dict:
    engagement_df["date_day"] = engagement_df["indexed_at"].dt.date
    engagement_df["post"] = (engagement_df["type"] == "post").astype(int)
    engagement_df["like"] = (engagement_df["type"] == "like").astype(int)
    engagement_df["repost"] = (engagement_df["type"] == "repost").astype(int)
    grouped_df = engagement_df.groupby("date_day", as_index=False)[
        ["post", "like", "repost"]
    ].sum()
    grouped_df = grouped_df.sort_values("date_day")
    grouped_df = grouped_df.set_index("date_day")
    grouped_df["post_past_30"] = grouped_df["post"].shift(1).rolling(window=30).sum()
    grouped_df["like_past_30"] = grouped_df["like"].shift(1).rolling(window=30).sum()
    grouped_df["repost_past_30"] = (
        grouped_df["repost"].shift(1).rolling(window=30).sum()
    )
    grouped_df = grouped_df.reset_index()
    grouped_df["engagements_past_30"] = (
        grouped_df["like_past_30"] + grouped_df["repost_past_30"]
    )
    return {
        "labels": grouped_df["date_day"].to_list(),
        "values": [
            x / y
            for x, y in zip(
                grouped_df["engagements_past_30"].to_list(),
                grouped_df["post_past_30"].to_list(),
            )
        ],
    }


def agg_engagement_by_hour(engagement_df: DataFrame) -> Dict:
    engagement_df["date_hour_part"] = engagement_df["indexed_at"].dt.hour
    engagement_df["date_day_part"] = engagement_df["indexed_at"].dt.day_of_week
    engagement_df["day_hour"] = (
        engagement_df["date_hour_part"] + engagement_df["date_day_part"] * 24
    )
    engagement_df["post"] = (engagement_df["type"] == "post").astype(int)
    engagement_df["like"] = (engagement_df["type"] == "like").astype(int)
    engagement_df["repost"] = (engagement_df["type"] == "repost").astype(int)
    grouped_df = engagement_df.groupby("day_hour", as_index=False)[
        ["post", "like", "repost"]
    ].sum()
    grouped_df["norm_post"] = grouped_df["post"] / grouped_df["post"].sum()
    grouped_df["norm_like"] = grouped_df["like"] / grouped_df["like"].sum()
    grouped_df["norm_repost"] = grouped_df["repost"] / grouped_df["repost"].sum()
    return {
        "labels": grouped_df["day_hour"].to_list(),
        "datasets": [
            {
                "label": "Post %",
                "data": grouped_df["norm_post"].to_list(),
                "backgroundColor": "rgba(255, 99, 132, 0.6)",
            },
            {
                "label": "Like %",
                "data": grouped_df["norm_like"].to_list(),
                "backgroundColor": "rgba(54, 162, 235, 0.6)",
            },
            {
                "label": "Repost %",
                "data": grouped_df["norm_repost"].to_list(),
                "backgroundColor": "rgba(255, 206, 86, 0.6)",
            },
        ],
    }


def cohort_curves_engagement(engagement_df: DataFrame) -> Dict:
    return {}
