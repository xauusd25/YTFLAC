import os
import re
import shutil

import yt_dlp
from yt_dlp.postprocessor.common import PostProcessor
from PIL import Image

# ... (existing comments/constants stay the same) ...


class CropThumbnailPP(PostProcessor):
    """Crops the downloaded thumbnail to a centered 1:1 square in place,
    before EmbedThumbnail picks it up."""

    def run(self, info):
        thumbnails = info.get("thumbnails") or []
        # The actual downloaded thumbnail file path(s) yt-dlp wrote to disk.
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
        img = img.convert("RGB") if img.mode in ("RGBA", "P") else img
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        cropped = img.crop((left, top, left + side, top + side))
        cropped.save(path)


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
