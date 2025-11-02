from typing import Dict, List

import pandas as pd
from atproto import Client

from scheduler.scheduler_utils import get_saved_schedule
from scheduler.schemas.scheduled_post import ImageConfig, ScheduledPost

IMAGE_CONFIG = ImageConfig(meta={})


class BlueskyScheduler:
    def __init__(self, handle, password, schedule_path):
        self.client = Client()
        self.client.login(handle, password)
        self.client_did = self.client.me.did
        self.schedule = get_saved_schedule(schedule_path)

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
                    image_config=IMAGE_CONFIG,
                )
            )
        return posts

    def _cleanup_schedule(self, post: ScheduledPost) -> Dict:
        image_path = post.path
        # Remove image from uploads folder
        # Remove row from schedule
        pass

    def _publish_post(self, post: ScheduledPost) -> Dict:
        text = post.text
        with open(post.path, "rb") as f:
            image = f.read()
        image_aspect_ratio = post.image_config
        print(text)
        print(image_aspect_ratio)
        out = {}
        # out = self.client.send_image(text, image, image_aspect_ratio)
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
