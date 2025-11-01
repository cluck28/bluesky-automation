import os
from typing import List

import pandas as pd
from atproto import Client
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_caching import Cache
from pandas import DataFrame
from werkzeug.utils import secure_filename

from analytics.aggregations import (
    agg_engagement_by_hour,
    agg_engagement_rate,
    agg_user_feed_dataframe,
    cohort_curves_likes,
    embed_type_agg_user_feed_dataframe,
    get_user_feed_df,
    stacked_agg_user_feed_dataframe,
)
from analytics.engagement import (
    get_engagement_df,
    get_engagement_score,
    get_likes_df,
    get_reposts_df,
    get_top_followers,
)
from analytics.top_posts import (
    get_most_bookmarked_post,
    get_most_liked_post,
    get_most_reposted_post,
)
from bluesky_client.get_author_feed import get_author_feed
from bluesky_client.get_post_likes import get_post_likes
from bluesky_client.get_post_reposts import get_post_reposts
from bluesky_client.get_profile import get_followers, get_follows, get_profile
from bluesky_client.schemas.profile import Profile

app = Flask(__name__)
app.config["CACHE_TYPE"] = "simple"  # or 'redis', 'filesystem', etc.
cache = Cache(app)

# Config
USER_HANDLE = os.getenv("CLIENT_USERNAME")
UPLOAD_PATH = "uploads"
WEB_PATH = os.path.abspath("./static")
UPLOAD_FOLDER = os.path.join(WEB_PATH, UPLOAD_PATH)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def login_client() -> tuple[Client, str]:
    client = Client()
    client_username = os.getenv("CLIENT_USERNAME")
    client_password = os.getenv("CLIENT_PASSWORD")
    client.login(client_username, client_password)
    client_did = client.me.did
    return client, client_did


@cache.cached(timeout=600, key_prefix="user_feed")
def get_user_feed() -> List:
    client, client_did = login_client()
    return get_author_feed(client, client_did)


@cache.cached(timeout=600, key_prefix="feed_df")
def get_user_feed_dataframe(user_feed: list, handle: str) -> DataFrame:
    return get_user_feed_df(user_feed, handle)


@cache.cached(timeout=600, key_prefix="user_profile")
def get_user_profile() -> Profile:
    client, client_did = login_client()
    return get_profile(client, client_did)


@cache.cached(timeout=600, key_prefix="user_follows")
def get_user_follows() -> list:
    client, client_did = login_client()
    return get_follows(client, client_did)


@cache.cached(timeout=600, key_prefix="user_followers")
def get_user_followers() -> list:
    client, client_did = login_client()
    return get_followers(client, client_did)


@cache.cached(timeout=3600, key_prefix="post_likes")
def get_user_post_likes(user_feed: list) -> list:
    client, _ = login_client()
    return get_post_likes(client, user_feed, USER_HANDLE)


@cache.cached(timeout=3600, key_prefix="likes_df")
def get_likes_dataframe(likes: list, follows: list, followers: list) -> DataFrame:
    return get_likes_df(likes, follows, followers)


@cache.cached(timeout=3600, key_prefix="post_reposts")
def get_user_post_reposts(user_feed: list) -> list:
    client, _ = login_client()
    return get_post_reposts(client, user_feed, USER_HANDLE)


@cache.cached(timeout=3600, key_prefix="reposts_df")
def get_reposts_dataframe(likes: list, follows: list, followers: list) -> DataFrame:
    return get_reposts_df(likes, follows, followers)


@cache.cached(timeout=3600, key_prefix="engagement_df")
def get_engagement_dataframe(
    feed_posts: dict, likes_df: DataFrame, reposts_df: DataFrame
) -> DataFrame:
    return get_engagement_df(feed_posts, likes_df, reposts_df, USER_HANDLE)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"
        file = request.files["file"]
        if file.filename == "":
            return "No selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return redirect(url_for("gallery"))
    return render_template("upload.html")


@app.route("/gallery")
def gallery():
    media_files = os.listdir(app.config["UPLOAD_FOLDER"])
    media_paths = [os.path.join(UPLOAD_PATH, f) for f in media_files]
    feed_posts = get_user_feed()
    external_paths = [thumb.embed.thumbnail for thumb in feed_posts]
    likes = [post.like_count for post in feed_posts]
    return render_template(
        "gallery.html",
        media_paths=media_paths,
        external_paths=external_paths,
        likes=likes,
    )


@app.route("/analytics", methods=["GET"])
def analytics():
    period = request.args.get("period", "month")  # default to month
    feed_posts = get_user_feed()
    feed_df = get_user_feed_dataframe(feed_posts, USER_HANDLE)
    user_profile = get_user_profile()
    handle = user_profile.handle
    followers_count = user_profile.followers_count
    following_count = user_profile.follows_count
    engagement_rate = get_engagement_score(feed_df, followers_count, period)
    total_likes = agg_user_feed_dataframe(
        feed_df, "total_likes", "like_count", "sum", period
    )
    likes = sum(total_likes["values"])
    total_posts = agg_user_feed_dataframe(
        feed_df, "total_posts", "like_count", "count", period
    )
    posts = sum(total_posts["values"])
    avg_likes = agg_user_feed_dataframe(
        feed_df, "average_likes", "like_count", "mean", period
    )
    average_likes = round(likes / posts, 0)
    stacked_totals = stacked_agg_user_feed_dataframe(feed_df, "sum", period)
    stacked_averages = stacked_agg_user_feed_dataframe(feed_df, "mean", period)
    top_liked_post_img, top_liked_post_count = get_most_liked_post(
        feed_posts, USER_HANDLE
    )
    top_bookmarked_post_img, top_bookmarked_post_count = get_most_bookmarked_post(
        feed_posts, USER_HANDLE
    )
    top_reposted_post_img, top_reposted_post_count = get_most_reposted_post(
        feed_posts, USER_HANDLE
    )
    avg_likes_by_type = embed_type_agg_user_feed_dataframe(
        feed_df, "average_likes", "like_count", "mean", period
    )
    return render_template(
        "analytics.html",
        handle=handle,
        followers=followers_count,
        following=following_count,
        posts=posts,
        engagement_rate=engagement_rate,
        average_likes=average_likes,
        top_liked_post_img=top_liked_post_img,
        top_likes_count=top_liked_post_count,
        top_bookmarked_post_img=top_bookmarked_post_img,
        top_bookmarked_count=top_bookmarked_post_count,
        top_reposted_post_img=top_reposted_post_img,
        top_reposted_count=top_reposted_post_count,
        total_likes=total_likes,
        avg_likes=avg_likes,
        total_posts=total_posts,
        stacked_totals=stacked_totals,
        stacked_averages=stacked_averages,
        average_likes_by_type=avg_likes_by_type,
    )


@app.route("/engagement", methods=["GET"])
def engagement():
    return render_template("engagement.html")


@app.route("/engagement/likes-data", methods=["GET"])
def engagement_likes_data():
    period = request.args.get("period", "month")  # default to month
    feed_posts = get_user_feed()
    likes_data = get_user_post_likes(feed_posts)
    followers = get_user_followers()
    follows = get_user_follows()
    likes_df = get_likes_dataframe(likes_data, follows, followers)
    reposts_data = get_user_post_reposts(feed_posts)
    reposts_df = get_reposts_dataframe(reposts_data, follows, followers)
    engagement_df = get_engagement_dataframe(feed_posts, likes_df, reposts_df)
    engagement_over_time = agg_engagement_rate(engagement_df, period)
    engagement_by_hour = agg_engagement_by_hour(engagement_df)
    cohort_curves = cohort_curves_likes(engagement_df, period)
    top_followers = get_top_followers(engagement_df, 15)
    return jsonify(
        {
            "engagement_over_time": engagement_over_time,
            "engagement_by_hour": engagement_by_hour,
            "cohort_curves": cohort_curves,
            "top_followers": top_followers,
        }
    )


@app.route("/schedule", methods=["GET", "POST"])
def schedule():
    return render_template("schedule.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5555)
