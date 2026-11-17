import io
import os

from mutagen.flac import FLAC, Picture
from PIL import Image

# ... (existing tag constants stay the same) ...


def _crop_square_bytes(data):
    """Crop raw image bytes to a centered 1:1 square, return new bytes + mime."""
    img = Image.open(io.BytesIO(data))
    img.load()

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    cropped = img.crop((left, top, left + side, top + side))

    buf = io.BytesIO()
    cropped.save(buf, format="JPEG", quality=95)
    return buf.getvalue(), "image/jpeg"


def _attach_thumbnail(audio, picture, thumb_url):
    """Download a thumbnail URL into a mutagen Picture, crop to 1:1, and attach it."""
    import urllib.request

    if thumb_url.startswith("http"):
        with urllib.request.urlopen(thumb_url, timeout=15) as resp:
            data = resp.read()
    else:
        with open(thumb_url, "rb") as fh:
            data = fh.read()

    cropped_data, mime = _crop_square_bytes(data)

    picture.data = cropped_data
    picture.mime = mime

    audio.add_picture(picture)
