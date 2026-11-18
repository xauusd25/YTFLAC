# 🎵 YTFLAC

<p align="center">
  <img src="thumbnail.png" alt="YTFLAC" width="640">
</p>

**YTFLAC** is a high-quality command-line audio downloader for **YouTube** and **YouTube Music**. It grabs the highest-fidelity audio stream available, transcodes it into a **FLAC Lossless** container, and embeds the thumbnail, metadata, and (when available) lyrics directly into the file.

<p align="center">
  <b>Developed by <a href="https://github.com/xauusd25">XAU_USD_25</a></b>
</p>

---

## ✨ Features

- 🎧 **FLAC Lossless Output** — best audio source transcoded to `.flac` (lossless container, compression level 8).
- 🖼️ **Embedded Artwork** — high-res thumbnail merged into every file.
- 🏷️ **Rich Metadata** — title, artist, album, year, genre, track number, composer, and more.
- 📂 **Playlists & Albums** — pass a playlist/album URL to grab everything.
- 🌐 **Cross-Platform** — macOS, Linux, Windows, and Android/Termux.

---

## 📥 Installation

Installers pull the latest **release archive (source zip)** from GitHub and install YTFLAC as a standalone tool via `uv` (with its own Python 3.12 and a bundled FFmpeg via `imageio-ffmpeg` — no admin rights needed).

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/xauusd25/YTFLAC/main/install.sh | bash
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/xauusd25/YTFLAC/main/install.ps1 | iex
```

### Android (Termux)

```bash
pkg update && yes | pkg upgrade
termux-setup-storage
curl -fsSL https://raw.githubusercontent.com/xauusd25/YTFLAC/main/install-termux.sh | bash
```

### Uninstall

```bash
# macOS / Linux / Termux
YTF_ACTION=uninstall bash -c "$(curl -fsSL https://raw.githubusercontent.com/xauusd25/YTFLAC/main/install.sh)"
```

```powershell
# Windows
$env:YTF_ACTION = 'uninstall'; irm https://raw.githubusercontent.com/xauusd25/YTFLAC/main/install.ps1 | iex
```

---

## 🚀 Usage

Just run `ytf` — it prompts you to paste a link, downloads the song to FLAC, then asks for the next one.

```bash
ytf
```

```
   _  __ ___   __  ____  _______ ____
  | |/ //   | / / / / / / / ___// __ \
  |   // /| |/ / / / / / /\__ \/ / / /
 /   |/ ___ / /_/ / /_/ /___/ / /_/ /
/_/|_/_/  |_\____/\____//____/_____/

╭─────────────────────────────────────────╮
│ YTFLAC v1.0.0 · DEV: XAU_USD_25         │
│ YouTube & YouTube Music → FLAC Lossless │
╰─────────────────────────────────────────╯
Downloads go to: /home/you/Downloads/YTFLAC
Paste a link (Ctrl+C to exit) >
```

- Paste a **YouTube / YouTube Music** link (song or playlist) and press **Enter**.
- After the download finishes, it prompts again for the next link.
- **Ctrl+C** exits the tool.

### Other options

```bash
# All files land in ~/Downloads/YTFLAC (per-platform Downloads folder).
# Override the output folder:
ytf -o ~/Music

# Check required dependencies:
ytf --check

# Show version:
ytf --version
```

Files are saved as `Title.flac` with embedded cover art and metadata. `ytflac` also works as a command; `ytf` is the short form (like `gig`).

---

## 🧱 Project Structure

```
YTFLAC/
├── ytflac/            # Python package
│   ├── __init__.py    # version & developer info
│   ├── downloader.py  # yt-dlp download + FLAC post-processing
│   ├── metadata.py    # mutagen tag/artwork embedding
│   ├── paths.py       # per-platform Downloads/YTFLAC folder
│   └── cli.py         # interactive loop + big banner
├── install.sh         # macOS / Linux / Termux installer
├── install.ps1        # Windows installer
├── pyproject.toml     # PEP 517 packaging + entry points
├── LICENSE            # MIT License
├── thumbnail.png      # repo banner
└── README.md
```

---

## ⚠️ Disclaimer

This tool is provided for **personal and educational use only**. Users are responsible for ensuring their downloads comply with applicable copyright laws and YouTube's Terms of Service. Please respect artists and support them by purchasing official releases.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  <b>Made with ❤️ by <a href="https://github.com/xauusd25">XAU_USD_25</a></b>
</p>
