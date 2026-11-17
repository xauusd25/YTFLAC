import argparse
import os

from rich.console import Console
from rich.panel import Panel

from . import __version__, DEV
from .downloader import download, DownloadError
from .metadata import apply_metadata

console = Console()

# Big ASCII-art logo, rendered like GigDownloader's big banner.
LOGO = r"""
   ____ ___ _____ ___   ___   ___
  /  _//   |  _  \_ _| / _ \ / _ \
  | | | | | | |_) ) | | | |_|| | | |
  | | | |_| |  _ <| | |  _|| |_| |
  \___\___/|_| \_\___\ \___/ \___/
"""


def print_banner():
    console.print(f"[bold cyan]{LOGO}[/bold cyan]")
    console.print(
        Panel(
            f"[bold cyan]YTFLAC v{__version__}[/bold cyan] · [bold magenta]DEV: {DEV}[/bold magenta]\n"
            "YouTube & YouTube Music → FLAC Lossless",
            expand=False,
        )
    )


def _fetch_lyrics_from_subtitles(info):
    """
    Attempt to recover lyrics from auto/manual subtitle tracks when present.
    Returns a plain-text string or None.
    """
    subs = info.get("subtitles") or {}
    auto = info.get("automatic_captions") or {}
    for lang, tracks in ({"*": subs} | {"*": auto}).items():
        for track in tracks or []:
            url = track.get("url")
            if not url:
                continue
            try:
                import urllib.request

                with urllib.request.urlopen(url, timeout=20) as resp:
                    text = resp.read().decode("utf-8", errors="replace")
                return _subtitle_to_lyrics(text)
            except Exception:
                continue
    return None


def _subtitle_to_lyrics(vtt):
    """Strip WebVTT/srv3 timing & cues down to plain lyric lines."""
    lines = []
    for raw in vtt.splitlines():
        line = raw.strip()
        if not line or line.startswith("WEBVTT") or "-->" in line:
            continue
        if line.startswith("Kind:") or line.startswith("Language:") or line.startswith("00:"):
            continue
        lines.append(line)
    return "\n".join(lines) if lines else None


def cmd_download(args):
    urls = args.urls
    out_dir = args.output or "."

    for url in urls:
        console.print(f"\n[bold]→ {url}[/bold]")
        try:
            paths = download(url, out_dir)
        except DownloadError as exc:
            console.print(f"[red]✗ {exc}[/red]")
            continue

        for path, info in paths:
            if not path or not path.lower().endswith(".flac"):
                continue
            console.print(f"  [cyan]Writing tags + artwork:[/cyan] {os.path.basename(path)}")
            try:
                lyrics = _fetch_lyrics_from_subtitles(info)
                apply_metadata(path, info, lyrics=lyrics)
                if lyrics:
                    console.print("  [magenta]Lyrics embedded.[/magenta]")
            except Exception as exc:
                console.print(f"  [yellow]Could not tag: {exc}[/yellow]")
        console.print(f"  [green]✔ Done → {out_dir}[/green]")

    console.print("\n[bold green]All requested items processed.[/bold green]")


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        prog="ytf",
        description="Download songs from YouTube & YouTube Music in FLAC Lossless.",
    )
    subparsers = parser.add_subparsers(dest="command")

    dl = subparsers.add_parser("download", aliases=["d"], help="Download song(s)/playlist")
    dl.add_argument("urls", nargs="+", help="YouTube/YT Music URL(s) or search query")
    dl.add_argument("-o", "--output", default=".", help="Output directory")
    dl.set_defaults(func=cmd_download)

    subparsers.add_parser("version", help="Show version").set_defaults(
        func=lambda _: console.print(f"YTFLAC {__version__} by {DEV}")
    )

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()