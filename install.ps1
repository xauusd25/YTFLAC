# YTFLAC Installer for Windows (PowerShell)
# Developed by XAU_USD_25
# Usage: irm https://raw.githubusercontent.com/xauusd25/YTFLAC/main/install.ps1 | iex

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  YTFLAC Installer - by XAU_USD_25" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# --- Ensure Python 3 is installed ---
$PY = Get-Command python -ErrorAction SilentlyContinue
if (-not $PY) {
    Write-Host "[ERROR] Python is not installed. Please install Python 3 from https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Python found: $($PY.Source)" -ForegroundColor Green

# --- Ensure ffmpeg is installed ---
$FFMPEG = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $FFMPEG) {
    Write-Host "[..] ffmpeg not found. Attempting to install via winget..." -ForegroundColor Yellow
    try {
        winget install -e --id Gyan.FFmpeg --accept-package-agreements --accept-source-agreements
    } catch {
        Write-Host "[WARN] Could not auto-install ffmpeg. Download it from https://ffmpeg.org" -ForegroundColor Yellow
    }
} else {
    Write-Host "[OK] ffmpeg found." -ForegroundColor Green
}

# --- Install YTFLAC ---
Write-Host "[..] Installing YTFLAC via pip..." -ForegroundColor Cyan
python -m pip install --upgrade "ytflac @ git+https://github.com/xauusd25/YTFLAC.git"

Write-Host "======================================" -ForegroundColor Green
Write-Host "  Installation complete!" -ForegroundColor Green
Write-Host "  Run: ytflac --help" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green