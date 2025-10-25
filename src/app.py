import os

from atproto import Client
from flask import Flask, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from bluesky_client.get_author_feed import get_author_feed

app = Flask(__name__)

# Config
UPLOAD_FOLDER = "./static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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
    client = Client()
    client_username = os.getenv("CLIENT_USERNAME")
    client_password = os.getenv("CLIENT_PASSWORD")
    client.login(client_username, client_password)
    client_did = client.me.did
    feed_posts = get_author_feed(client, client_did)
    external_paths = [thumb.embed.thumbnail for thumb in feed_posts]
    return render_template(
        "gallery.html", media_paths=media_paths, external_paths=external_paths
    )


if __name__ == "__main__":
    app.run(debug=True)
