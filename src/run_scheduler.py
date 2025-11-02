from config import (
    QUEUE_RULES_FILE_PATH,
    SCHEDULE_FILE_PATH,
    USER_HANDLE,
    USER_PASSWORD,
    WEB_PATH,
)
from scheduler.scheduler import BlueskyScheduler

if __name__ == "__main__":
    scheduler = BlueskyScheduler(
        USER_HANDLE, USER_PASSWORD, WEB_PATH, SCHEDULE_FILE_PATH, QUEUE_RULES_FILE_PATH
    )
    scheduler.run()
