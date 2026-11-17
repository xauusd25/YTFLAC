#!/usr/bin/env bash
# =====================================================================
#  YTFLAC Installer for macOS / Linux / Termux  (by XAU_USD_25)
# =====================================================================
#  Install / update:
#      curl -fsSL https://raw.githubusercontent.com/xauusd25/YTFLAC/main/install.sh | bash
#
#  Uninstall:
#      YTF_ACTION=uninstall bash -c "$(curl -fsSL https://raw.githubusercontent.com/xauusd25/YTFLAC/main/install.sh)"
#
#  No admin rights needed. Python, ffmpeg and yt-dlp are installed for you
#  via `uv` — ffmpeg is bundled by imageio-ffmpeg, so nothing extra is needed.
# =====================================================================

set -e

Action="${YTF_ACTION:-install}"
Repo="xauusd25/YTFLAC"
AppZip="https://github.com/$Repo/archive/refs/heads/main.zip"

# ---------- Colors / helpers ----------
if [ -t 1 ]; then
    N=$'\e[0m'; R=$'\e[1;38;5;196m'; G=$'\e[1;38;5;82m'
    Y=$'\e[1;38;5;220m'; C=$'\e[1;38;5;51m'; W=$'\e[1;38;5;255m'
    GRAY=$'\e[38;5;244m'; LAV=$'\e[1;38;5;183m'; TEAL=$'\e[1;38;5;80m'
else
    N=''; R=''; G=''; Y=''; C=''; W=''; GRAY=''; LAV=''; TEAL=''
fi
CHK=$'\xe2\x9c\x94'; CROSS=$'\xe2\x9c\x98'; PLAY=$'\xe2\x96\xb6'; DOT=$'\xe2\x80\xa2'

banner() {
    echo
    printf '%s\n' "${LAV}    ____ ___ _____ ___   ___   ___"
    printf '%s\n' "${LAV}   /  _//   |  _  \_ _| / _ \ / _ \"
    printf '%s\n' "${LAV}   | | | | | | |_) ) | | | | || | | |"
    printf '%s\n' "${LAV}   | | | |_| |  _ <| | | |_| | |_| |"
    printf '%s\n' "${LAV}   \___\___/|_| \_\___\ \___/ \___/${N}"
    echo "              ${TEAL}FLAC Downloader Installer${N}"
    echo
}

fail() { echo " ${R}${CROSS} ${N}${R}$1${N}"; exit 1; }
ok()   { echo " ${G}${CHK} ${N}${G}$1${N}"; }
warn() { echo " ${Y}${DOT} ${N}${Y}$1${N}"; }
step() { echo; echo " ${C}${PLAY} ${N}${W}$1${N}"; }

# ---------------- Uninstall ----------------
if [ "$Action" = "uninstall" ]; then
    banner
    step "Removing YTFLAC"
    if command -v uv >/dev/null 2>&1; then
        uv tool uninstall ytflac || true
    fi
    if command -v ytf >/dev/null 2>&1; then
        rm -f "$(command -v ytf)" 2>/dev/null || true
    fi
    ok "YTFLAC removed"
    echo
    exit 0
fi

banner

# ---------------- Check / install uv ----------------
step "Checking for uv (Python package manager)"
if ! command -v uv >/dev/null 2>&1; then
    warn "uv not found — installing it"
    if command -v curl >/dev/null 2>&1; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    elif command -v wget >/dev/null 2>&1; then
        wget -qO- https://astral.sh/uv/install.sh | sh
    else
        fail "Need curl or wget to install uv"
    fi
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi
ok "uv ready: $(uv --version 2>/dev/null)"

# ---------------- Install the app from the release zip ----------------
step "Downloading & installing YTFLAC from source zip"
uv tool install --force --reinstall \
    --python 3.12 \
    --with 'yt-dlp[default]' \
    --with imageio-ffmpeg \
    "ytflac @ $AppZip"

# Add uv bin dir to PATH if missing
UVBIN="$(uv tool dir --bin 2>/dev/null || echo "$HOME/.local/bin")"
case ":$PATH:" in
    *":$UVBIN:"*) ;;
    *) export PATH="$UVBIN:$PATH" ;;
esac
ok "Command added: ytf"

echo
echo " ${G}══════════════════════════════════════════════${N}"
echo " ${G}${CHK} Installation completed successfully${N}"
echo " ${G}══════════════════════════════════════════════${N}"
echo
echo " ${Y}${PLAY} Start it by typing:${N}"
echo "    ${C}ytf${N}"
echo
echo " ${GRAY}Also available:${N} ytflac · ytf --check · ytf --help"
echo