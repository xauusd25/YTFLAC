import os
import re
import shutil

import yt_dlp
import yt_dlp.postprocessor as ytdlp_pp
from yt_dlp.postprocessor.common import PostProcessor
from PIL import Image

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


class CropThumbnailPP(PostProcessor):
    """Crops the downloaded thumbnail to a centered 1:1 square in place,
    before EmbedThumbnail picks it up."""

    def run(self, info):
        thumbnails = info.get("thumbnails") or []
        candidates = []
        if info.get("thumbnail_filepath"):
            candidates.append(info["thumbnail_filepath"])
        for t in thumbnails:
            fp = t.get("filepath")
            if fp:
                candidates.append(fp)

        seen = set()
        for path in candidates:
            if not path or path in seen or not os.path.exists(path):
                continue
            seen.add(path)
            try:
                self._crop_square(path)
                self.to_screen(f"Cropped thumbnail to 1:1: {os.path.basename(path)}")
            except Exception as exc:
                self.report_warning(f"Could not crop thumbnail {path}: {exc}")

        return [], info

    @staticmethod
    def _crop_square(path):
        img = Image.open(path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        cropped = img.crop((left, top, left + side, top + side))
        cropped.save(path)


# Make the custom postprocessor discoverable by its "key" string, the same
# way yt-dlp resolves its own built-in postprocessors.
ytdlp_pp.CropThumbnailPP = CropThumbnailPP


def _base_ydl_opts(output_dir):
    return {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "quiet": False,
        "no_warnings": False,
        "noplaylist": False,
        "writethumbnail": True,
        "postprocessors": [
            # Extract the best audio stream and transcode to FLAC.
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "flac",
                "preferredquality": "0",
            },
            # Crop thumbnail to 1:1 BEFORE it gets embedded.
            {
                "key": "CropThumbnail",
            },
            # Attach the (now-square) thumbnail into the file itself.
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
