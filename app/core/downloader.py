import re
import threading
from dataclasses import dataclass
from typing import Callable

import yt_dlp

from .netopts import NetOptions
from .paths import ffmpeg_location


class Cancelled(Exception):
    pass


@dataclass
class Progress:
    percent: float = 0.0
    speed: str = ""
    eta: str = ""
    status: str = ""


_ANSI = re.compile(r"\x1b\[[0-9;]*m")

# Bilibili's CDN (Tencent EdgeOne) answers Python's plain full-file GET with HTTP 567
# but accepts the same request when it carries a Range header, so download in ranged chunks.
BILIBILI_CHUNK = 10 * 1024 * 1024


def _is_bilibili(url: str) -> bool:
    return any(h in url for h in ("bilibili.com", "b23.tv", "bilivideo.com"))


def friendly_error(exc: Exception) -> str:
    msg = _ANSI.sub("", str(exc))
    low = msg.lower()
    if "sign in" in low or "login" in low or "cookies" in low:
        return "此內容需要登入，請在設定中啟用瀏覽器 cookies。"
    if "geo" in low or "not available in your country" in low:
        return "此內容有地區限制。"
    if "unsupported url" in low:
        return "不支援此網址。"
    if "ffmpeg" in low:
        return "找不到 ffmpeg，無法合併影音。"
    return msg.replace("ERROR: ", "")


def build_opts(fmt: str, outdir: str, template: str = "%(title).150B [%(id)s].%(ext)s",
               net: NetOptions | None = None) -> dict:
    opts: dict = {
        "outtmpl": f"{outdir}/{template}",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "merge_output_format": "mp4",
        "windowsfilenames": True,
        "retries": 5,
    }
    if fmt in ("mp3", "m4a"):
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": fmt, "preferredquality": "192"}]
    else:
        opts["format"] = fmt
    (net or NetOptions()).apply(opts)
    loc = ffmpeg_location()
    if loc:
        opts["ffmpeg_location"] = loc
    return opts


def download(url: str, fmt: str, outdir: str, on_progress: Callable[[Progress], None],
             cancel: threading.Event, template: str | None = None,
             net: NetOptions | None = None) -> str:
    """Download one URL. Returns the final file path. Raises Cancelled on cancel."""
    kwargs = {"template": template} if template else {}
    opts = build_opts(fmt, outdir, net=net, **kwargs)
    if _is_bilibili(url):
        opts["http_chunk_size"] = BILIBILI_CHUNK

    def hook(d: dict) -> None:
        if cancel.is_set():
            raise Cancelled()
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            pct = d["downloaded_bytes"] / total * 100 if total else 0.0
            on_progress(Progress(pct, _ANSI.sub("", d.get("_speed_str", "")).strip(),
                                 _ANSI.sub("", d.get("_eta_str", "")).strip(), "下載中"))
        elif d["status"] == "finished":
            on_progress(Progress(100.0, "", "", "處理中"))

    opts["progress_hooks"] = [hook]
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            if fmt in ("mp3", "m4a"):
                path = path.rsplit(".", 1)[0] + "." + fmt
            elif not path.lower().endswith(".mp4"):
                path = path.rsplit(".", 1)[0] + ".mp4"
            return path
    except yt_dlp.utils.DownloadError as e:
        if cancel.is_set() or "Cancelled" in str(e):
            raise Cancelled() from e
        raise
