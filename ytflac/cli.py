import argparse
import os
import sys

from rich.console import Console
from rich.panel import Panel

from . import __version__, DEV
from .downloader import download, DownloadError
from .metadata import apply_metadata
from .paths import download_dir

console = Console()

# Big italic-style ASCII-art logo.
LOGO = r"""
   _  __ ___   __  ____  _______ ____
  | |/ //   | / / / / / / / ___// __ \
  |   // /| |/ / / / / / /\__ \/ / / /
 /   |/ ___ / /_/ / /_/ /___/ / /_/ /
/_/|_/_/  |_\____/\____//____/_____/
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


def _handle(url, out_dir):
    """Download one URL and report the result."""
    console.print(f"\n[bold]→ {url}[/bold]")
    try:
        results = download(url, out_dir)
    except DownloadError as exc:
        console.print(f"[red]✗ {exc}[/red]")
        return

    for path, info in results:
        if not path:
            continue
        if path.lower().endswith(".flac"):
            try:
                apply_metadata(path, info)
            except Exception as exc:
                console.print(f"  [yellow]Could not tag: {exc}[/yellow]")
        console.print(f"  [green]✔ {os.path.basename(path)}[/green]")
    console.print(f"  [cyan]Saved in:[/cyan] [bold]{out_dir}[/bold]")


def run(out_dir):
    """
    Interactive loop: keep asking for a link, download it, then ask again.
    Only Ctrl+C exits.
    """
    while True:
        try:
            url = input("Paste a link (Ctrl+C to exit) > ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print(f"\n\n[teal]Thanks for using YTFLAC. Bye![/teal]")
            return

        if not url:
            continue
        _handle(url, out_dir)


def cmd_check(_args):
    """Verify required runtime dependencies are present."""
    import shutil

    checks = []
    ffmpeg = shutil.which("ffmpeg")
    checks.append(("ffmpeg", ffmpeg, "required for audio transcode + thumbnail"))

    for mod in ("yt_dlp", "mutagen", "rich"):
        try:
            __import__(mod)
            checks.append((mod, True, "python package"))
        except ImportError:
            checks.append((mod, False, "python package"))

    all_ok = True
    for name, present, why in checks:
        if present:
            console.print(f"  [green]✔ {name}[/green]  {why}")
        else:
            console.print(f"  [red]✗ {name}[/red]  missing ({why})")
            all_ok = False
    return 0 if all_ok else 1


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        prog="ytf",
        description="Download songs from YouTube & YouTube Music in FLAC Lossless.",
    )
    parser.add_argument("-o", "--output", default=None, help="Output folder (default: ~/Downloads/YTFLAC)")
    parser.add_argument("--check", action="store_true", help="Check required dependencies and exit")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    args = parser.parse_args()

    if args.version:
        console.print(f"YTFLAC {__version__} by {DEV}")
        return
    if args.check:
        cmd_check(args)
        return

    out_dir = download_dir(args.output)
    console.print(f"[dim]Downloads go to:[/dim] [bold]{out_dir}[/bold]")

    try:
        run(out_dir)
    except (KeyboardInterrupt, EOFError):
        console.print(f"\n\n[teal]Thanks for using YTFLAC. Bye![/teal]")
        sys.exit(0)


if __name__ == "__main__":
    main()