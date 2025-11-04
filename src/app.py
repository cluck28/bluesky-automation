import os
from typing import List

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
    agg_post_engagement_by_post_day,
    agg_post_engagement_by_post_hour,
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
from config import (
    ALLOWED_EXTENSIONS,
    RULES_FOLDER,
    SCHEDULE_FOLDER,
    UPLOAD_FOLDER,
    UPLOAD_PATH,
    USER_HANDLE,
    USER_PASSWORD,
)
from scheduler.scheduler_utils import (
    get_saved_schedule,
    update_queue_rules,
    update_saved_schedule,
)

app = Flask(__name__)
app.config["CACHE_TYPE"] = "simple"  # or 'redis', 'filesystem', etc.
cache = Cache(app)

# Config
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def login_client() -> tuple[Client, str]:
    client = Client()
    client.login(USER_HANDLE, USER_PASSWORD)
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
            schedule = get_saved_schedule(SCHEDULE_FOLDER)
            schedule.append(
                {
                    "path": os.path.join(UPLOAD_PATH, filename),
                    "text": None,
                    "date": None,
                    "status": None,
                }
            )
            update_saved_schedule(SCHEDULE_FOLDER, RULES_FOLDER, schedule)
            return redirect(url_for("gallery"))
    return render_template("upload.html")


@app.route("/gallery")
def gallery():
    media_paths = get_saved_schedule(SCHEDULE_FOLDER)
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
    post_engagement_by_post_day = agg_post_engagement_by_post_day(feed_df)
    post_engagement_by_post_hour = agg_post_engagement_by_post_hour(feed_df)
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
        post_engagement_by_post_day=post_engagement_by_post_day,
        post_engagement_by_post_hour=post_engagement_by_post_hour,
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
    media_items = get_saved_schedule(SCHEDULE_FOLDER)
    return render_template("schedule.html", media_items=media_items)


@app.route("/add_rule", methods=["GET", "POST"])
def add_rule():
    data = request.get_json()
    new_rule = data.get("rule", [])
    update_queue_rules(RULES_FOLDER, new_rule)
    update_saved_schedule(SCHEDULE_FOLDER, RULES_FOLDER)
    return jsonify({"success": True})


@app.route("/update_order", methods=["GET", "POST"])
def update_order():
    data = request.get_json()
    old_schedule = get_saved_schedule(SCHEDULE_FOLDER)
    min_date = min([item["date"] for item in old_schedule])
    new_schedule = []
    i = 0
    for item in data.get("order", []):
        for old_entries in old_schedule:
            if old_entries["path"] == item:
                old_text = old_entries["text"]
        if i == 0:
            new_schedule.append(
                {"path": item, "text": old_text, "date": min_date, "status": None}
            )
        else:
            new_schedule.append(
                {"path": item, "text": old_text, "date": None, "status": None}
            )
        i += 1
    update_saved_schedule(SCHEDULE_FOLDER, RULES_FOLDER, new_schedule)
    media_items = get_saved_schedule(SCHEDULE_FOLDER)
    return render_template("_sortable_list.html", media_items=media_items)


@app.route("/update_text", methods=["POST"])
def update_text():
    data = request.get_json()
    media_id = data.get("id")
    new_text = data.get("text", "").strip()
    old_schedule = get_saved_schedule(SCHEDULE_FOLDER)
    new_schedule = []
    for item in old_schedule:
        if media_id == item["path"]:
            new_schedule.append(
                {
                    "path": item["path"],
                    "text": new_text,
                    "date": item["date"],
                    "status": item["status"],
                }
            )
        else:
            new_schedule.append(
                {
                    "path": item["path"],
                    "text": item["text"],
                    "date": item["date"],
                    "status": item["status"],
                }
            )
    update_saved_schedule(SCHEDULE_FOLDER, RULES_FOLDER, new_schedule)
    render_schedule = get_saved_schedule(SCHEDULE_FOLDER)
    return render_template("_sortable_list.html", media_items=render_schedule)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5555)
