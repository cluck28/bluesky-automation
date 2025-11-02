from typing import List

from atproto import Client

from scheduler.scheduler_utils import get_saved_schedule
from scheduler.schemas.scheduled_post import ImageConfig, ScheduledPost


class BlueskyScheduler:
    def __init__(self, handle, password, schedule_path):
        self.client = Client()
        self.client.login(handle, password)
        self.client_did = self.client.me.did
        self.schedule = get_saved_schedule(schedule_path)

    def _validate_post(self, post: ScheduledPost) -> bool:
        pass

    def _get_posts(self) -> List[ScheduledPost]:
        pass

    def _cleanup_schedule(self):
        pass

    def _publish_post(self, post):
        pass

    def run(self):
        posts = self._get_posts()
        for post in posts:
            if self._validate_post(post):
                try:
                    self._publish_post(post)
                except ValueError:
                    raise ValueError
        pass
