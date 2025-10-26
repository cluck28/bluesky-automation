import os
from typing import List

import pandas as pd
from atproto import Client
from flask import Flask, redirect, render_template, request, url_for
from flask_caching import Cache
from pandas import DataFrame
from werkzeug.utils import secure_filename

from analytics.aggregations import (
    agg_user_feed_dataframe,
    get_user_feed_df,
    stacked_agg_user_feed_dataframe,
)
from analytics.top_posts import (
    get_most_bookmarked_post,
    get_most_liked_post,
    get_most_reposted_post,
)
from bluesky_client.get_author_feed import get_author_feed
from bluesky_client.get_profile import get_followers, get_follows, get_profile
from bluesky_client.schemas.profile import Follower, Profile

app = Flask(__name__)
app.config["CACHE_TYPE"] = "simple"  # or 'redis', 'filesystem', etc.
cache = Cache(app)

# Config
USER_HANDLE = os.getenv("CLIENT_USERNAME")
UPLOAD_FOLDER = "./static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@cache.cached(timeout=600, key_prefix="user_feed")
def get_user_feed() -> List:
    client = Client()
    client_username = os.getenv("CLIENT_USERNAME")
    client_password = os.getenv("CLIENT_PASSWORD")
    client.login(client_username, client_password)
    client_did = client.me.did
    return get_author_feed(client, client_did)


@cache.cached(timeout=600, key_prefix="feed_df")
def get_user_feed_dataframe(user_feed: list, handle: str) -> DataFrame:
    return get_user_feed_df(user_feed, handle)


@cache.cached(timeout=600, key_prefix="user_profile")
def get_user_profile() -> Profile:
    client = Client()
    client_username = os.getenv("CLIENT_USERNAME")
    client_password = os.getenv("CLIENT_PASSWORD")
    client.login(client_username, client_password)
    client_did = client.me.did
    return get_profile(client, client_did)


@cache.cached(timeout=600, key_prefix="user_follows")
def get_user_follows() -> Follower:
    client = Client()
    client_username = os.getenv("CLIENT_USERNAME")
    client_password = os.getenv("CLIENT_PASSWORD")
    client.login(client_username, client_password)
    client_did = client.me.did
    return get_follows(client, client_did)


@cache.cached(timeout=600, key_prefix="user_followers")
def get_user_followers() -> Follower:
    client = Client()
    client_username = os.getenv("CLIENT_USERNAME")
    client_password = os.getenv("CLIENT_PASSWORD")
    client.login(client_username, client_password)
    client_did = client.me.did
    return get_followers(client, client_did)


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
    media_paths = [os.path.join(app.config["UPLOAD_FOLDER"], f) for f in media_files]
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
    followers = user_profile.followers_count
    following = user_profile.follows_count
    engagement_rate = 100
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
    print(average_likes)
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
    return render_template(
        "analytics.html",
        handle=handle,
        followers=followers,
        following=following,
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
    )


if __name__ == "__main__":
    app.run(debug=True)
