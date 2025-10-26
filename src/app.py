import os
from typing import List

import pandas as pd
from atproto import Client
from flask import Flask, redirect, render_template, request, url_for
from flask_caching import Cache
from pandas import DataFrame
from werkzeug.utils import secure_filename

from analytics.aggregations import (agg_user_feed_dataframe, get_user_feed_df,
                                    stacked_agg_user_feed_dataframe)
from bluesky_client.get_author_feed import get_author_feed

app = Flask(__name__)
app.config["CACHE_TYPE"] = "simple"  # or 'redis', 'filesystem', etc.
cache = Cache(app)

# Config
USER_HANDLE = os.getenv("CLIENT_HANDLE")
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
    total_likes = agg_user_feed_dataframe(
        feed_df, "total_likes", "like_count", "sum", period
    )
    total_posts = agg_user_feed_dataframe(
        feed_df, "total_posts", "like_count", "count", period
    )
    avg_likes = agg_user_feed_dataframe(
        feed_df, "average_likes", "like_count", "mean", period
    )
    stacked_totals = stacked_agg_user_feed_dataframe(feed_df, "sum", period)
    stacked_averages = stacked_agg_user_feed_dataframe(feed_df, "mean", period)
    return render_template(
        "analytics.html",
        total_likes=total_likes,
        avg_likes=avg_likes,
        total_posts=total_posts,
        stacked_totals=stacked_totals,
        stacked_averages=stacked_averages,
    )


if __name__ == "__main__":
    app.run(debug=True)
