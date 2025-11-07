import io
import os
import re
from typing import Dict, List

import pandas as pd
from atproto import Client, client_utils
from atproto_client.models.app.bsky.embed.defs import AspectRatio
from PIL import Image, ImageOps
from pydantic import ValidationError

from scheduler.scheduler_utils import get_saved_schedule, update_saved_schedule
from scheduler.schemas.scheduled_post import ScheduledPost


def prepare_image_for_bluesky_upload(
    image_data: bytes,
    size_limit_bytes: int = 976_560,  # 1 MB
    step_quality: int = 5,
    min_quality: int = 40,
    resize_factor: float = 0.9,
):
    """
    Normalize, compress, and resize image until under size_limit_bytes.
    Returns (compressed_bytes, width, height, quality).
    """

    # --- Step 1: Normalize orientation (fix sideways EXIF images)
    img = Image.open(io.BytesIO(image_data))
    img = ImageOps.exif_transpose(img)  # apply rotation per EXIF
    img = img.convert("RGB")  # ensure consistent color mode

    quality = 95
    width, height = img.size

    # --- Step 2: Iteratively reduce size
    while True:
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        size = buffer.tell()

        if size <= size_limit_bytes or (quality <= min_quality and width < 500):
            buffer.seek(0)
            print(
                f"✅ Ready for upload: {size/1024:.1f} KB | {width}x{height} | q={quality}"
            )
            return buffer.getvalue(), AspectRatio(width=width, height=height)

        if quality > min_quality:
            quality -= step_quality
        else:
            # downscale dimensions proportionally
            width = int(width * resize_factor)
            height = int(height * resize_factor)
            img = img.resize((width, height), Image.LANCZOS)
            quality = 90  # reset slightly higher to avoid over-blurring


class BlueskyScheduler:
    def __init__(self, handle, password, web_path, schedule_folder, rules_folder):
        self.client = Client()
        self.client.login(handle, password)
        self.web_path = web_path
        self.schedule_path = os.path.join(web_path, schedule_folder)
        self.rules_path = os.path.join(web_path, rules_folder)
        self.schedule = get_saved_schedule(os.path.join(web_path, schedule_folder))

    def _get_posts(self) -> List[ScheduledPost]:
        df = pd.DataFrame(self.schedule)
        df["date"] = pd.to_datetime(df["date"])
        df = df[df["date"] <= pd.Timestamp.today()]
        posts = []
        for record in df.to_dict(orient="records"):
            try:
                posts.append(
                    ScheduledPost(
                        path=record["path"],
                        text=record["text"],
                        date=record["date"],
                        status=record["status"],
                    )
                )
            except ValidationError:
                raise ValidationError
        return posts

    def _cleanup_schedule(self, post: ScheduledPost) -> Dict:
        df = pd.DataFrame(self.schedule)
        df = df[df["path"] != post.path]
        df[["path", "text", "date", "status"]].to_csv(self.schedule_path, index=False)
        update_saved_schedule(self.schedule_path, self.rules_path)
        return

    def _send_image(self, text, file_path):
        tb = client_utils.TextBuilder()
        parts = re.split(r"(?=(?:#[\w]+))|(?<=[\w])(?=#)", text)
        print(parts)
        for part in parts:
            if "#" not in part:
                tb.text(part)
            else:
                tb.tag(part, part.strip("#"))

        # Build the image embed
        with open(file_path, "rb") as f:
            image = f.read()

        # Resize
        compressed_image, aspect_ratio = prepare_image_for_bluesky_upload(image)

        try:
            result = self.client.send_image(
                text=tb.build_text(),
                image=compressed_image,
                image_alt="",
                facets=tb.build_facets(),
                image_aspect_ratio=aspect_ratio,
            )
        except Exception:
            return None
        return result

    def _publish_post(self, post: ScheduledPost) -> Dict:
        try:
            file_path = os.path.join(self.web_path, post.path)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Image file not found: {file_path}")
            # Need to format the text correctly
            # Need to write alt text
            out = self._send_image(post.text, file_path)
            return out.uri
        except FileNotFoundError as e:
            print(f"Publish failed: missing image file — {e}")
            return None
        except PermissionError as e:
            print(f"Publish failed: permission error — {e}")
            return None
        except AttributeError as e:
            print(f"Publish failed: unexpected client response — {e}")
            return None
        except Exception as e:
            print(f"Unexpected error publishing post: {e}")
            return None

    def run(self):
        if not self.schedule:
            print("No posts scheduled")
            return
        try:
            posts = self._get_posts()
        except ValidationError:
            print("Validation of posts failed")
            return
        for post in posts:
            post_uri = self._publish_post(post)
            if post_uri:
                print(f"Post uploaded {post_uri}")
                try:
                    self._cleanup_schedule(post)
                    print("Cleaned up schedule")
                except KeyError:
                    print("Unable to clean up schedule after posting")
                    return
            else:
                print(f"Uploading post failed for post: {post}")
                continue
        return
