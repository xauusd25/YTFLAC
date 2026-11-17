import io
import os

from mutagen.flac import FLAC, Picture
from PIL import Image

# FLAC stores tag data as Vorbis comments.

# Tag names (vorbis comments are ASCII-case-insensitive on read).
TITLE = "title"
ARTIST = "artist"
ALBUM = "album"
ALBUM_ARTIST = "albumartist"
DATE = "date"
YEAR = "year"
GENRE = "genre"
TRACK_NUMBER = "tracknumber"
DISCNUMBER = "discnumber"
COMPOSER = "composer"
LYRICIST = "lyricist"
COMMENT = "comment"


def _norm(value):
    """Normalize a tag value to a list of strings, dropping empties."""
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        vals = [str(v) for v in value if v]
    else:
        vals = [str(value)]
    return vals if vals else None


def apply_metadata(file_path, info):
    """
    Apply metadata (title/artist/album/etc.) and embed cover art into a FLAC
    file.

    `info` is the yt-dlp info dict. Returns True on success.
    """
    if not os.path.exists(file_path) or not file_path.lower().endswith(".flac"):
        raise FileNotFoundError(f"Expected a FLAC file, got: {file_path}")

    audio = FLAC(file_path)

    mapping = {
        TITLE: info.get("title"),
        ARTIST: info.get("artist") or info.get("uploader"),
        ALBUM: info.get("album") or info.get("album_name"),
        ALBUM_ARTIST: info.get("album_artist"),
        DATE: info.get("release_date") or info.get("upload_date"),
        GENRE: info.get("genre"),
        TRACK_NUMBER: info.get("track_number") or info.get("track"),
        DISCNUMBER: info.get("disc_number"),
        COMPOSER: info.get("composer"),
        LYRICIST: info.get("writer"),
    }

    # If the extractor gave no year, fall back to the upload date's first 4
    # characters (YYYYMMDD -> YYYY).
    if not mapping[DATE] and info.get("upload_date"):
        mapping[DATE] = info["upload_date"][:4]

    for key, value in mapping.items():
        normed = _norm(value)
        if normed:
            audio[key] = normed

    # Description or "too much" header line as a comment, if present.
    if info.get("description"):
        audio[COMMENT] = _norm(info["description"][:200])

    # --- Cover art embedding ---
    # yt-dlp's EmbedThumbnail already writes a picture block, but if it is
    # missing (or the local thumbnail file exists), attach it here.
    thumb = info.get("thumbnail") or info.get("thumbnails", [{}])[-1].get("url")
    if not audio.pictures and thumb:
        picture = Picture()
        picture.type = 3  # front cover
        picture.mime = "image/jpeg"
        picture.desc = "Cover"
        try:
            _attach_thumbnail(audio, picture, thumb)
        except Exception:
            # Non-fatal: skip cover art if it cannot be fetched.
            pass

    audio.save()
    return True


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
    """Download a thumbnail URL, crop it to 1:1, and attach it as a mutagen Picture."""
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
