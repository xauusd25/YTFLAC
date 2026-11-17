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
- 📝 **Lyrics** — auto-captions/subtitles converted to embedded `LYRICS` tags when present.
- 📂 **Playlists & Albums** — pass a playlist/album URL to grab everything.
- 🖥️ **Big Banner CLI** — a large ASCII-art logo, beautiful output powered by `Rich`.
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
termux-setup-storage
curl -fsSL https://raw.githubusercontent.com/xauusd25/YTFLAC/main/install.sh | bash
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

```bash
# Download a single song
ytf download https://youtube.com/watch?v=VIDEO_ID

# YouTube Music
ytf download https://music.youtube.com/watch?v=VIDEO_ID

# Download a whole playlist / album
ytf download https://youtube.com/playlist?list=PLAYLIST_ID

# Specify an output folder
ytf download -o ~/Music https://youtube.com/watch?v=VIDEO_ID

# Download several items at once
ytf download URL1 URL2 URL3

# Show version
ytf version
```

All files are written as `Title.flac` with embedded cover art, metadata, and lyrics.

> `ytflac` also works as a command; `ytf` is the short form (like `gig`).

---

## 🧱 Project Structure

```
YTFLAC/
├── ytflac/            # Python package
│   ├── __init__.py    # version & developer info
│   ├── downloader.py  # yt-dlp download + FLAC post-processing
│   ├── metadata.py    # mutagen tag/art/lyric embedding
│   └── cli.py         # command-line interface + big banner
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