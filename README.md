# 🎵 YTFLAC

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
- 💻 **Clean CLI** — beautiful output powered by `Rich`.
- 🌐 **Cross-Platform** — macOS, Linux, Windows, and Android/Termux.

---

## 🖥️ Supported Platforms

| Platform | Install method | Command |
|----------|---------------|---------|
| **macOS / Linux** | `curl` script | `curl -fsSL https://raw.githubusercontent.com/xauusd25/YTFLAC/main/install.sh \| bash` |
| **Windows (PowerShell)** | `irm` script | `irm https://raw.githubusercontent.com/xauusd25/YTFLAC/main/install.ps1 \| iex` |
| **Android (Termux)** | `curl` script | `curl -fsSL https://raw.githubusercontent.com/xauusd25/YTFLAC/main/install.sh \| bash` |
| **Any (source)** | `pip install .` | `git clone https://github.com/xauusd25/YTFLAC.git && cd YTFLAC && pip install .` |

---

## 📦 Requirements

- **Python 3.8+**
- **FFmpeg** — required for audio transcoding and thumbnail embedding.

The install scripts detect and install FFmpeg automatically where possible.

---

## 🚀 Usage

```bash
# Download a single song
ytflac download https://youtube.com/watch?v=VIDEO_ID

# YouTube Music
ytflac download https://music.youtube.com/watch?v=VIDEO_ID

# Download a whole playlist / album
ytflac download https://youtube.com/playlist?list=PLAYLIST_ID

# Specify an output folder
ytflac download -o ~/Music https://youtube.com/watch?v=VIDEO_ID

# Download several items at once
ytflac download URL1 URL2 URL3

# Show version
ytflac version
```

All files are written as `Title.flac` with embedded cover art, metadata, and lyrics.

---

## 🧱 Project Structure

```
YTFLAC/
├── ytflac/            # Python package
│   ├── __init__.py    # version & developer info
│   ├── downloader.py  # yt-dlp download + FLAC post-processing
│   ├── metadata.py    # mutagen tag/art/lyric embedding
│   └── cli.py         # argparse command-line interface
├── install.sh         # macOS / Linux / Termux installer
├── install.ps1        # Windows installer
├── pyproject.toml     # PEP 517/518 packaging
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