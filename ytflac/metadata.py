import os

from mutagen.flac import FLAC, Picture

# FLAC stores tag data as Vorbis comments. Lyrics conventionally live in a
# "LYRICS" comment field (many players also honor "UNSYNCEDLYRICS").

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
LYRICS = "lyrics"
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


def apply_metadata(file_path, info, lyrics=None):
    """
    Apply metadata (title/artist/album/etc.), embed cover art, and attach
    lyrics to a FLAC file.

    `info` is the yt-dlp info dict. `lyrics`, when provided, is attached to
    the LYRICS field. Returns True on success.
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

    # --- Lyrics embedding ---
    if lyrics:
        audio[LYRICS] = [lyrics]

    audio.save()
    return True


def _attach_thumbnail(audio, picture, thumb_url):
    """Download a thumbnail URL into a mutagen Picture and attach it."""
    import urllib.request

    if thumb_url.startswith("http"):
        with urllib.request.urlopen(thumb_url, timeout=15) as resp:
            data = resp.read()
    else:
        with open(thumb_url, "rb") as fh:
            data = fh.read()

    picture.data = data
    if data[:3] == b"\xff\xd8\xff":
        picture.mime = "image/jpeg"
    elif data[:8] == b"\x89PNG\r\n\x1a\n":
        picture.mime = "image/png"
    else:
        picture.mime = "application/octet-stream"

    audio.add_picture(picture)


def read_lyrics(file_path):
    """Return the embedded lyrics of a FLAC file, or None."""
    audio = FLAC(file_path)
    for key in (LYRICS, "unsyncedlyrics"):
        if key in audio and audio[key]:
            return "\n".join(audio[key])
    return None