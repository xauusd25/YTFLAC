#!/usr/bin/env bash
# =====================================================================
#  YTFLAC Installer for Termux (pip-based)  (by XAU_USD_25)
# =====================================================================
#  Install / update:
#      curl -fsSL https://raw.githubusercontent.com/xauusd25/YTFLAC/main/install-termux.sh | bash
#
#  Uninstall:
#      YTF_ACTION=uninstall bash -c "$(curl -fsSL https://raw.githubusercontent.com/xauusd25/YTFLAC/main/install-termux.sh)"
#
#  Unlike install.sh (which uses uv), this installer uses Termux's own
#  `pkg` package manager for system deps (python, ffmpeg, git) and plain
#  `pip` for the Python package itself. Use this one specifically on
#  Termux/Android.
# =====================================================================

set -e

Action="${YTF_ACTION:-install}"
Repo="xauusd25/YTFLAC"
AppZip="https://github.com/$Repo/archive/refs/heads/main.zip"

# ---------- Colors / helpers ----------
if [ -t 1 ]; then
    N=$'\e[0m'; R=$'\e[1;38;5;196m'; G=$'\e[1;38;5;82m'
    Y=$'\e[1;38;5;220m'; C=$'\e[1;38;5;51m'; W=$'\e[1;38;5;255m'
    GRAY=$'\e[38;5;244m'; TEAL=$'\e[1;38;5;80m'
else
    N=''; R=''; G=''; Y=''; C=''; W=''; GRAY=''; TEAL=''
fi
CHK=$'\xe2\x9c\x94'; CROSS=$'\xe2\x9c\x98'; PLAY=$'\xe2\x96\xb6'; DOT=$'\xe2\x80\xa2'

banner() {
    echo
    cat <<'YTFLAC_LOGO'
   _  __ ___   __  ____  _______ ____
  | |/ //   | / / / / / / / ___// __ \
  |   // /| |/ / / / / / /\__ \/ / / /
 /   |/ ___ / /_/ / /_/ /___/ / /_/ /
/_/|_/_/  |_\____/\____//____/_____/
YTFLAC_LOGO
    echo "         ${TEAL}FLAC Downloader Installer (Termux)${N}"
    echo
}

fail() { echo " ${R}${CROSS} ${N}${R}$1${N}"; exit 1; }
ok()   { echo " ${G}${CHK} ${N}${G}$1${N}"; }
warn() { echo " ${Y}${DOT} ${N}${Y}$1${N}"; }
step() { echo; echo " ${C}${PLAY} ${N}${W}$1${N}"; }

# Run a command quietly: swallow its stdout/stderr, but if it fails, show
# what it printed (so real errors aren't hidden, just the normal noise).
quiet_run() {
    local log
    log="$(mktemp)"
    if "$@" >"$log" 2>&1; then
        rm -f "$log"
        return 0
    else
        echo " ${R}${CROSS} Command failed: $*${N}"
        cat "$log"
        rm -f "$log"
        return 1
    fi
}

# ---------------- Confirm we're actually on Termux ----------------
if [ -z "$PREFIX" ] || [ "${PREFIX#*com.termux}" = "$PREFIX" ]; then
    warn "This doesn't look like a Termux environment (no \$PREFIX/com.termux detected)."
    warn "On regular Linux/macOS, use install.sh instead."
fi

# ---------------- Uninstall ----------------
if [ "$Action" = "uninstall" ]; then
    banner
    step "Removing YTFLAC"
    quiet_run pip uninstall -y ytflac || true
    if command -v ytf >/dev/null 2>&1; then
        rm -f "$(command -v ytf)" 2>/dev/null || true
    fi
    ok "YTFLAC removed"
    echo
    exit 0
fi

banner

# ---------------- System packages via pkg ----------------
step "Installing system dependencies via pkg"
quiet_run pkg update -y || warn "pkg update had warnings (continuing)"
quiet_run pkg install -y \
    python \
    python-pip \
    python-pillow \
    ffmpeg \
    git \
    libffi \
    openssl \
    || fail "pkg install failed"
ok "System dependencies ready"
# python / python-pip  -> interpreter + pip itself
# python-pillow        -> prebuilt Termux package; pulling this via pkg
#                         instead of letting pip compile Pillow from
#                         source is what makes this installer fast.
#                         Compiling Pillow on-device with clang is the
#                         single slowest step otherwise (can take many
#                         minutes on phone hardware).
# ffmpeg               -> audio transcode + thumbnail embedding
# git                  -> some pip deps are pulled/built from source
# libffi / openssl     -> needed by cryptography-related pip deps
#                         (e.g. pycryptodomex, used by yt-dlp)

# ---------------- pip itself ----------------
# NOTE: do NOT run `pip install --upgrade pip` on Termux — pip is managed
# by the python-pip pkg package there, and self-upgrading it is blocked
# ("Installing pip is forbidden, this will break the python-pip package").
# Whatever pip version `pkg install python-pip` gave us above is used as-is.
step "Checking pip"
ok "pip ready: $(pip --version)"

# ---------------- Install the app + Python deps via pip ----------------
step "Installing YTFLAC and Python dependencies via pip"
# No --force-reinstall on the shared deps: that flag makes pip rebuild and
# redownload EVERYTHING on every run, even packages that already match.
# Only ytflac itself (the thing that actually changes release to release)
# is force-reinstalled; yt-dlp/mutagen/rich are left alone if already
# satisfied, and Pillow is skipped entirely since python-pillow (pkg,
# prebuilt) already provides it.
quiet_run pip install --upgrade \
    "yt-dlp[default]" \
    mutagen \
    rich \
    || fail "pip install failed (deps)"
quiet_run pip install --upgrade --force-reinstall --no-deps \
    "ytflac @ $AppZip" \
    || fail "pip install failed (ytflac)"
ok "YTFLAC installed"

# ---------------- PATH check ----------------
PYBIN="$(python -c 'import sysconfig; print(sysconfig.get_path("scripts"))' 2>/dev/null || echo "$PREFIX/bin")"
case ":$PATH:" in
    *":$PYBIN:"*) ;;
    *) export PATH="$PYBIN:$PATH" ;;
esac

if command -v ytf >/dev/null 2>&1; then
    ok "Command added: ytf"
else
    warn "ytf not found on PATH yet — restart Termux or run: source ~/.bashrc"
fi

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
