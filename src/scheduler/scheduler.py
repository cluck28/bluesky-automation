import io
import os
import re
from typing import Dict, List

import pandas as pd
from atproto import Client, client_utils
from PIL import Image
from pydantic import ValidationError

from scheduler.scheduler_utils import get_saved_schedule, update_saved_schedule
from scheduler.schemas.scheduled_post import ScheduledPost


def compress_image_for_upload(
    image_data: bytes,
    size_limit_bytes: int = 1_048_576,
    step_quality: int = 5,
    min_quality: int = 40,
    resize_factor: float = 0.9,
) -> bytes:
    """
    Iteratively compress an image (from bytes) until it's under size_limit_bytes.
    Returns final JPEG bytes suitable for upload (no disk writes).

    Parameters:
        image_data (bytes): Original image data (any format).
        size_limit_bytes (int): Max allowed size (default 1 MB).
        step_quality (int): How much to lower quality per iteration.
        min_quality (int): Minimum JPEG quality threshold.
        resize_factor (float): Scale factor for downscaling if needed.
    """
    img = Image.open(io.BytesIO(image_data)).convert("RGB")
    quality = 95
    width, height = img.size

    while True:
        # Save to memory buffer
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        size = buffer.tell()

        if size <= size_limit_bytes or (quality <= min_quality and width < 500):
            buffer.seek(0)
            print(
                f"✅ Compressed: {size/1024:.1f} KB | quality={quality} | {width}x{height}"
            )
            return buffer.getvalue()

        # Try reducing quality first
        if quality > min_quality:
            quality -= step_quality
        else:
            # If quality too low, downscale image
            width = int(width * resize_factor)
            height = int(height * resize_factor)
            img = img.resize((width, height), Image.LANCZOS)
            quality = 90  # reset quality upward to regain some sharpness


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
        compressed_image = compress_image_for_upload(image)

        try:
            result = self.client.send_image(
                text=tb.build_text(),
                image=compressed_image,
                image_alt="",
                facets=tb.build_facets(),
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
