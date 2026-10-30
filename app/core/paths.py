import os
import shutil
import sys
from pathlib import Path


def app_dir() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home())
    d = Path(base) / "ytdlpgui"
    d.mkdir(parents=True, exist_ok=True)
    return d


def bundled_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parents[2]


def ffmpeg_location() -> str | None:
    local = bundled_root() / "bin" / "ffmpeg.exe"
    if local.exists():
        return str(local.parent)
    found = shutil.which("ffmpeg")
    return str(Path(found).parent) if found else None
