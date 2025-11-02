import os

from dotenv import load_dotenv

load_dotenv()


USER_HANDLE = os.getenv("CLIENT_USERNAME")
USER_PASSWORD = os.getenv("CLIENT_USERNAME")
UPLOAD_PATH = "uploads"
WEB_PATH = os.path.abspath("./src/static")
UPLOAD_FOLDER = os.path.join(WEB_PATH, UPLOAD_PATH)
SCHEDULE_FILE_PATH = "schedule/schedule.csv"
QUEUE_RULES_FILE_PATH = "schedule/rules.csv"
SCHEDULE_FOLDER = os.path.join(WEB_PATH, SCHEDULE_FILE_PATH)
RULES_FOLDER = os.path.join(WEB_PATH, QUEUE_RULES_FILE_PATH)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4"}
