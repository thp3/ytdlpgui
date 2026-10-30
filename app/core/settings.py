import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .paths import app_dir


@dataclass
class Settings:
    download_dir: str = str(Path.home() / "Downloads")
    max_parallel: int = 2
    cookies_browser: str = ""  # "", "chrome", "edge", "firefox"
    cookies_file: str = ""
    proxy: str = ""

    @classmethod
    def load(cls) -> "Settings":
        f = app_dir() / "settings.json"
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except (OSError, ValueError):
            return cls()

    def save(self) -> None:
        (app_dir() / "settings.json").write_text(
            json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8")
