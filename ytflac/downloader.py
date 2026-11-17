import os
import re
import shutil

import yt_dlp

# yt-dlp doesn't stream native FLAC from YouTube; the source streams are
# Opus/M4A. To deliver "FLAC Lossless" output, we grab the highest-fidelity
# audio available and losslessly transcode it into a FLAC container via ffmpeg.
# No audio data is discarded during the container transcode beyond what the
# source already provides.

# Regexes to tag an input as YouTube Music / YouTube / playlist / search.
YT_MUSIC_HOST = "music.youtube.com"
YT_HOST = ("youtube.com", "youtu.be")


class DownloadError(Exception):
    """Raised when a download fails for a recoverable reason."""


def _base_ydl_opts(output_dir):
    return {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "quiet": False,
        "no_warnings": False,
        "noplaylist": False,
        "writethumbnail": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en", "en-US", "en-orig"],
        "subtitlesformat": "srv3/best",
        "postprocessors": [
            # Extract the best audio stream and transcode to FLAC.
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "flac",
                "preferredquality": "0",
            },
            # Attach the downloaded thumbnail into the file itself.
            {
                "key": "EmbedThumbnail",
            },
            # Copy over all standard metadata fields from the extractor.
            {
                "key": "FFmpegMetadata",
                "add_metadata": True,
            },
        ],
        "ffmpeg_location": shutil.which("ffmpeg") or "ffmpeg",
        "postprocessor_args": {
            "FFmpegExtractAudio": ["-c:a", "flac", "-compression_level", "8"],
        },
    }


def _classify(url):
    """Return a short label describing the platform the URL belongs to."""
    if YT_MUSIC_HOST in url:
        return "YouTube Music"
    if any(host in url for host in YT_HOST):
        return "YouTube"
    return "URL"


def is_playlist(url):
    """Best-effort heuristic for playlist / album URLs."""
    return any(token in url for token in ("playlist", "list=", "album"))


def download(url, output_dir="."):
    """
    Download a single song, playlist, album, or search query into `output_dir`
    and post-process it to FLAC with embedded thumbnail + metadata.

    Returns a list of (filepath, info) tuples, one per downloaded entry.
    """
    os.makedirs(output_dir, exist_ok=True)
    platform = _classify(url)

    opts = _base_ydl_opts(output_dir)
    if not is_playlist(url):
        # Only the exact item, never a whole playlist, unless explicitly a
        # playlist/album URL.
        opts["noplaylist"] = True

    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except Exception as exc:  # yt-dlp raises DownloadError subclasses
            raise DownloadError(f"Failed to download ({platform}): {exc}") from exc

        entries = info if isinstance(info, dict) and "entries" in info else [info]
        results = []
        for e in entries:
            if not e:
                continue
            filepath = (e.get("requested_downloads") or [{}])[0].get("filepath")
            if not filepath:
                filepath = ydl.prepare_filename(e)
            results.append((filepath, e))
        return results