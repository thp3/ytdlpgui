import atexit
import os
import shutil
import tempfile
from dataclasses import dataclass


def _private_copy(path: str) -> str:
    """yt-dlp rewrites its cookie file on exit, so work on a throwaway copy of the user's file."""
    fd, tmp = tempfile.mkstemp(prefix="ytdlpgui_cookies_", suffix=".txt")
    os.close(fd)
    shutil.copyfile(path, tmp)
    atexit.register(lambda: os.path.exists(tmp) and os.remove(tmp))
    return tmp


@dataclass(frozen=True)
class NetOptions:
    cookies_file: str = ""
    cookies_browser: str = ""
    proxy: str = ""

    def apply(self, opts: dict) -> dict:
        if self.cookies_file:
            opts["cookiefile"] = _private_copy(self.cookies_file)
        elif self.cookies_browser:
            opts["cookiesfrombrowser"] = (self.cookies_browser,)
        if self.proxy:
            opts["proxy"] = self.proxy
        return opts
