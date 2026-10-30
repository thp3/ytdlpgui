import logging
import traceback

from .paths import app_dir

_log = logging.getLogger("ytdlpgui")
if not _log.handlers:
    _h = logging.FileHandler(app_dir() / "error.log", encoding="utf-8")
    _h.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    _log.addHandler(_h)
    _log.setLevel(logging.INFO)


def log_exception(context: str, exc: BaseException) -> None:
    _log.error("%s\n%s", context, "".join(traceback.format_exception(exc)))
