#!/usr/bin/env bash
# YTFLAC Installer for macOS / Linux / Termux
# Developed by XAU_USD_25
# Usage: curl -fsSL https://raw.githubusercontent.com/xauusd25/YTFLAC/main/install.sh | bash

set -e

echo "======================================"
echo "  YTFLAC Installer - by XAU_USD_25"
echo "======================================"

# --- Detect package manager & install ffmpeg if missing ---
check_ffmpeg() {
    if command -v ffmpeg >/dev/null 2>&1; then
        echo "[OK] ffmpeg already installed."
        return 0
    fi
    echo "[..] ffmpeg not found. Installing..."
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update -y && sudo apt-get install -y ffmpeg
    elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y ffmpeg
    elif command -v pacman >/dev/null 2>&1; then
        sudo pacman -S --noconfirm ffmpeg
    elif command -v brew >/dev/null 2>&1; then
        brew install ffmpeg
    elif command -v pkg >/dev/null 2>&1; then
        # Termux
        pkg install -y ffmpeg python
    else
        echo "[WARN] Could not auto-install ffmpeg. Please install it manually."
    fi
}

# --- Ensure Python 3 ---
check_python() {
    if command -v python3 >/dev/null 2>&1; then
        PY=python3
    elif command -v python >/dev/null 2>&1; then
        PY=python
    else
        echo "[ERROR] Python 3 is required. Please install it first."
        exit 1
    fi
}

# --- Install YTFLAC ---
check_ffmpeg
check_python

echo "[..] Installing YTFLAC via pip..."
$PY -m pip install --upgrade "ytflac @ git+https://github.com/xauusd25/YTFLAC.git" \
    || $PY -m pip install --user "ytflac @ git+https://github.com/xauusd25/YTFLAC.git"

echo "[OK] YTFLAC installed successfully!"
echo ""
echo "======================================"
echo "  Installation complete!"
echo "  Run: ytflac --help"
echo "======================================"