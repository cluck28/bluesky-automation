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
    df = feed_df.copy()
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
    df = feed_df.copy()
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
    df = feed_df.copy()
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


def agg_engagement_rate(engagement_df: DataFrame, period: str) -> Dict:
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
    df = engagement_df.copy()
    df["date_day"] = df["indexed_at"].dt.date
    df["post"] = (df["type"] == "post").astype(int)
    df["like"] = (df["type"] == "like").astype(int)
    df["repost"] = (df["type"] == "repost").astype(int)
    grouped_df = df.groupby("date_day", as_index=False)[
        ["post", "like", "repost"]
    ].sum()
    grouped_df = grouped_df.sort_values("date_day")
    grouped_df = grouped_df.set_index("date_day")
    grouped_df["post_past_30"] = (
        grouped_df["post"].shift(1).rolling(window=window).sum()
    )
    grouped_df["like_past_30"] = (
        grouped_df["like"].shift(1).rolling(window=window).sum()
    )
    grouped_df["repost_past_30"] = (
        grouped_df["repost"].shift(1).rolling(window=window).sum()
    )
    grouped_df = grouped_df.reset_index()
    grouped_df["engagements_past_30"] = (
        grouped_df["like_past_30"] + grouped_df["repost_past_30"]
    )
    return {
        "labels": grouped_df["date_day"].to_list(),
        "values": [
            x / y if y != 0 else 0
            for x, y in zip(
                grouped_df["engagements_past_30"].fillna(0).to_list(),
                grouped_df["post_past_30"].fillna(0).to_list(),
            )
        ],
    }


def agg_engagement_by_hour(engagement_df: DataFrame) -> Dict:
    df = engagement_df.copy()
    df["date_hour_part"] = df["indexed_at"].dt.hour
    df["date_day_part"] = df["indexed_at"].dt.day_of_week
    df["day_hour"] = df["date_hour_part"] + df["date_day_part"] * 24
    df["post"] = (df["type"] == "post").astype(int)
    df["like"] = (df["type"] == "like").astype(int)
    df["repost"] = (df["type"] == "repost").astype(int)
    grouped_df = df.groupby("day_hour", as_index=False)[
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


def cohort_curves_likes(engagement_df: DataFrame, period: str) -> Dict:
    df = engagement_df.copy()
    df["hours_to_engagement"] = round(
        (df["indexed_at"] - df["post_indexed_at"]).dt.total_seconds() / 3600, 0
    )
    df_filtered = df[
        (df["type"] == "like")
        & (df["hours_to_engagement"] > 0)
        & (df["hours_to_engagement"] <= 504)
    ]
    if period == "day":
        df_filtered["cohort"] = (
            df_filtered["post_indexed_at"].dt.to_period("D").astype(str)
        )
    elif period == "week":
        df_filtered["cohort"] = (
            df_filtered["post_indexed_at"].dt.to_period("W").astype(str)
        )
    elif period == "month":
        df_filtered["cohort"] = (
            df_filtered["post_indexed_at"].dt.to_period("M").astype(str)
        )
    elif period == "quarter":
        df_filtered["cohort"] = (
            df_filtered["post_indexed_at"].dt.to_period("Q").astype(str)
        )
    elif period == "year":
        df_filtered["cohort"] = (
            df_filtered["post_indexed_at"].dt.to_period("Y").astype(str)
        )
    else:
        df_filtered["cohort"] = (
            df_filtered["post_indexed_at"].dt.to_period("M").astype(str)
        )
    cohort_curve = (
        df_filtered.groupby("cohort")
        .apply(
            lambda x: x["hours_to_engagement"].value_counts().sort_index().cumsum()
            / len(x)
        )
        .unstack(0)
        .reset_index()
    )
    filter_cohort_curve = cohort_curve[cohort_curve["hours_to_engagement"] <= 168]
    filled_cohort_curve = filter_cohort_curve.ffill()
    last_three_cols = filled_cohort_curve.columns[-3:].to_list()
    return {
        "labels": filled_cohort_curve["hours_to_engagement"].to_list(),
        "datasets": [
            {
                "label": last_three_cols[0],
                "data": filled_cohort_curve[last_three_cols[0]].to_list(),
                "backgroundColor": "rgba(255, 99, 132, 0.6)",
            },
            {
                "label": last_three_cols[1],
                "data": filled_cohort_curve[last_three_cols[1]].to_list(),
                "backgroundColor": "rgba(54, 162, 235, 0.6)",
            },
            {
                "label": last_three_cols[2],
                "data": filled_cohort_curve[last_three_cols[2]].to_list(),
                "backgroundColor": "rgba(255, 206, 86, 0.6)",
            },
        ],
    }


def agg_post_engagement_by_post_day(feed_df: DataFrame) -> Dict:
    df = feed_df.copy()
    df["date_day_part"] = df["indexed_at"].dt.day_of_week
    grouped_df = df.groupby("date_day_part", as_index=False)["like_count"].mean()
    return {
        "labels": grouped_df["date_day_part"].to_list(),
        "values": grouped_df["like_count"].to_list(),
    }


def agg_post_engagement_by_post_hour(feed_df: DataFrame) -> Dict:
    df = feed_df.copy()
    df["date_hour_part"] = df["indexed_at"].dt.hour
    grouped_df = df.groupby("date_hour_part", as_index=False)["like_count"].mean()
    return {
        "labels": grouped_df["date_hour_part"].to_list(),
        "values": grouped_df["like_count"].to_list(),
    }
