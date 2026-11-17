import os
import sys
from pathlib import Path

# All downloads go into a YTFLAC folder inside the platform's Downloads dir.
YTFLAC_FOLDER = "YTFLAC"


def is_termux() -> bool:
    """Detect Android Termux by its env markers."""
    return "com.termux" in os.environ.get("PREFIX", "") or "TERMUX_VERSION" in os.environ


def _windows_downloads() -> Path:
    """The real Downloads folder, even if the user moved it (registry)."""
    try:
        import winreg

        key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
            value, _ = winreg.QueryValueEx(k, "{374DE290-123F-4565-9164-39C4925E467B}")
        return Path(os.path.expandvars(value))
    except Exception:
        return Path.home() / "Downloads"


def _xdg_downloads() -> Path:
    """Linux: honour the XDG user-dirs setting (localized/moved Downloads)."""
    config_home = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    cfg = Path(config_home) / "user-dirs.dirs"
    try:
        for line in cfg.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("XDG_DOWNLOAD_DIR="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                value = value.replace("$HOME", str(Path.home()))
                if value:
                    return Path(value)
    except OSError:
        pass
    return Path.home() / "Downloads"


def default_download_base() -> Path:
    """The system's Downloads folder. A YTFLAC subfolder is used inside it."""
    override = os.environ.get("YTF_DOWNLOAD_DIR")
    if override:
        return Path(override).expanduser()

    if is_termux():
        # Termux shared storage is available after `termux-setup-storage`.
        shared = Path.home() / "storage" / "downloads"
        return shared if shared.is_dir() else Path.home() / "Downloads"
    if sys.platform.startswith("win"):
        return _windows_downloads()
    if sys.platform == "darwin":
        return Path.home() / "Downloads"
    return _xdg_downloads()


def _usable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        return os.access(path, os.W_OK)
    except OSError:
        return False


def download_dir(preferred=None) -> Path:
    """
    Resolve the single directory every downloaded file lands in.

    Order: explicit --output, $YTF_DOWNLOAD_DIR, then the platform Downloads
    folder. Returns <Downloads>/YTFLAC on the first writable base; as a last
    resort falls back to ./YTFLAC.
    """
    bases = []
    if preferred:
        bases.append(Path(preferred).expanduser())
    bases += [default_download_base(), Path.home(), Path.cwd()]

    for base in bases:
        target = base / YTFLAC_FOLDER
        if _usable(target):
            return target
    return Path.cwd() / YTFLAC_FOLDER