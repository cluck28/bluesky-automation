import os

from scheduler.scheduler import BlueskyScheduler

SCHEDULE_PATH = ""


if __name__ == "__main__":
    handle = os.getenv("CLIENT_USERNAME")
    password = os.getenv("CLIENT_PASSWORD")
    scheduler = BlueskyScheduler(handle, password, SCHEDULE_PATH)
    scheduler.run()
