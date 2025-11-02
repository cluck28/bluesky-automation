import os
from typing import Dict, List

import pandas as pd
from atproto import Client

from scheduler.scheduler_utils import get_saved_schedule
from scheduler.schemas.scheduled_post import ImageConfig, ScheduledPost


class BlueskyScheduler:
    def __init__(self, handle, password, web_path, schedule_folder):
        self.client = Client()
        self.client.login(handle, password)
        self.web_path = web_path
        self.schedule = get_saved_schedule(os.path.join(web_path, schedule_folder))

    def _validate_post(self, post: ScheduledPost) -> bool:
        return True

    def _get_posts(self) -> List[ScheduledPost]:
        df = pd.DataFrame(self.schedule)
        df["date"] = pd.to_datetime(df["date"])
        df = df[df["date"] <= pd.Timestamp.today()]
        posts = []
        for record in df.to_dict(orient="records"):
            posts.append(
                ScheduledPost(
                    path=record["path"],
                    text=record["text"],
                    date=record["date"],
                    status=record["status"],
                )
            )
        return posts

    def _cleanup_schedule(self, post: ScheduledPost) -> Dict:
        image_path = post.path
        # Remove image from uploads folder
        # Remove row from schedule
        pass

    def _publish_post(self, post: ScheduledPost) -> Dict:
        with open(os.path.join(self.web_path, post.path), "rb") as f:
            image = f.read()
        out = {}
        # out = self.client.send_image(post.text, image)
        return out

    def run(self):
        posts = self._get_posts()
        print(posts)
        for post in posts:
            if self._validate_post(post):
                try:
                    res = self._publish_post(post)
                    print(res)
                except ValueError:
                    raise ValueError
        pass
