from dataclasses import dataclass, field

import yt_dlp

from .netopts import NetOptions
from .paths import ffmpeg_location


@dataclass
class QualityOption:
    label: str
    format: str
    height: int = 0


@dataclass
class VideoInfo:
    url: str
    title: str
    uploader: str
    duration: int
    thumbnail: str
    extractor: str
    qualities: list[QualityOption] = field(default_factory=list)
    entries: list["VideoInfo"] = field(default_factory=list)
    is_playlist: bool = False


AUDIO_OPTIONS = [
    QualityOption("僅音訊 (mp3)", "mp3"),
    QualityOption("僅音訊 (m4a)", "m4a"),
]


def _qualities(info: dict) -> list[QualityOption]:
    heights = sorted(
        {f["height"] for f in info.get("formats", []) if f.get("height") and f.get("vcodec") != "none"},
        reverse=True,
    )
    opts = [QualityOption("最佳畫質", "bv*+ba/b")]
    for h in heights:
        opts.append(QualityOption(f"{h}p", f"bv*[height<={h}]+ba/b[height<={h}]", h))
    return opts + AUDIO_OPTIONS


def _base(url: str, info: dict) -> VideoInfo:
    return VideoInfo(
        url=info.get("webpage_url") or info.get("url") or url,
        title=info.get("title") or url,
        uploader=info.get("uploader") or info.get("channel") or "",
        duration=int(info.get("duration") or 0),
        thumbnail=info.get("thumbnail") or "",
        extractor=info.get("extractor_key") or "",
    )


def extract(url: str, net: NetOptions | None = None) -> VideoInfo:
    opts = {"quiet": True, "no_warnings": True, "skip_download": True, "extract_flat": "in_playlist"}
    (net or NetOptions()).apply(opts)
    loc = ffmpeg_location()
    if loc:
        opts["ffmpeg_location"] = loc
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    if info is None:
        raise ValueError("無法解析此網址")
    if info.get("_type") == "playlist":
        v = _base(url, info)
        v.is_playlist = True
        for e in info.get("entries") or []:
            if not e:
                continue
            child = _base(e.get("url") or url, e)
            child.url = e.get("url") or e.get("webpage_url") or child.url
            v.entries.append(child)
        v.qualities = [QualityOption("最佳畫質", "bv*+ba/b")] + AUDIO_OPTIONS
        return v
    v = _base(url, info)
    v.qualities = _qualities(info)
    return v
