import os

from dotenv import load_dotenv

from scheduler.scheduler import BlueskyScheduler

load_dotenv()

WEB_PATH = os.path.abspath("./static")
SCHEDULE_FILE_PATH = "schedule/schedule.csv"
SCHEDULE_FOLDER = os.path.join(WEB_PATH, SCHEDULE_FILE_PATH)
HANDLE = os.getenv("CLIENT_USERNAME")
PASSWORD = os.getenv("CLIENT_PASSWORD")


if __name__ == "__main__":
    scheduler = BlueskyScheduler(HANDLE, PASSWORD, SCHEDULE_FOLDER)
    scheduler.run()
