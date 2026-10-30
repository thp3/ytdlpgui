import threading

from app.core.downloader import Cancelled, build_opts, download, friendly_error
from app.core import downloader


def test_build_opts_video():
    o = build_opts("bv*+ba/b", "out")
    assert o["format"] == "bv*+ba/b" and "postprocessors" not in o


def test_build_opts_audio():
    o = build_opts("mp3", "out")
    assert o["postprocessors"][0]["preferredcodec"] == "mp3"


def test_friendly_error():
    assert "登入" in friendly_error(Exception("ERROR: Sign in to confirm"))
    assert "不支援" in friendly_error(Exception("Unsupported URL: x"))


def test_cancel_before_progress(monkeypatch, tmp_path):
    ev = threading.Event()
    ev.set()

    class Fake:
        def __init__(self, opts): self.opts = opts
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def extract_info(self, url, download):
            self.opts["progress_hooks"][0]({"status": "downloading", "downloaded_bytes": 1})

    monkeypatch.setattr(downloader.yt_dlp, "YoutubeDL", Fake)
    try:
        download("u", "bv*+ba/b", str(tmp_path), lambda p: None, ev)
        assert False
    except Cancelled:
        pass


def test_netoptions_file_beats_browser_and_proxy(tmp_path):
    from app.core.netopts import NetOptions
    src = tmp_path / "c.txt"
    src.write_text("# Netscape HTTP Cookie File\n")
    o = NetOptions(str(src), "chrome", "http://127.0.0.1:7890").apply({})
    assert o["proxy"] == "http://127.0.0.1:7890" and "cookiesfrombrowser" not in o
    assert o["cookiefile"] != str(src) and open(o["cookiefile"]).read() == src.read_text()


def test_netoptions_browser_and_empty():
    from app.core.netopts import NetOptions
    assert NetOptions("", "edge", "").apply({}) == {"cookiesfrombrowser": ("edge",)}
    assert NetOptions().apply({}) == {}


def test_build_opts_applies_net(tmp_path):
    from app.core.netopts import NetOptions
    src = tmp_path / "c.txt"
    src.write_text("x")
    o = build_opts("bv*+ba/b", "out", net=NetOptions(str(src), "", "socks5://h:1"))
    assert o["cookiefile"] != str(src) and o["proxy"] == "socks5://h:1"


def test_bilibili_uses_ranged_chunks_only_there(monkeypatch, tmp_path):
    seen = {}

    class Fake:
        def __init__(self, opts): seen.update(opts)
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def extract_info(self, url, download): return {"ext": "mp4"}
        def prepare_filename(self, info): return str(tmp_path / "v.mp4")

    monkeypatch.setattr(downloader.yt_dlp, "YoutubeDL", Fake)
    download("https://www.bilibili.com/video/av1", "bv*+ba/b", str(tmp_path), lambda p: None, threading.Event())
    assert seen["http_chunk_size"] == downloader.BILIBILI_CHUNK
    seen.clear()
    download("https://www.tiktok.com/@a/video/1", "bv*+ba/b", str(tmp_path), lambda p: None, threading.Event())
    assert "http_chunk_size" not in seen


def test_sanitize_path_drops_untraversable_entries(monkeypatch, tmp_path):
    import os
    from app.core import pathenv
    good, bad = tmp_path / "good", tmp_path / "bad"
    good.mkdir()
    bad.mkdir()
    real = os.scandir

    def fake(p):
        if str(p) == str(bad):
            raise OSError(448, "untrusted mount point")
        return real(p)

    monkeypatch.setattr(pathenv.os, "scandir", fake)
    env = {"PATH": os.pathsep.join([str(good), str(bad), ""])}
    assert pathenv.sanitize_path(env) == [str(bad)]
    assert env["PATH"] == str(good)
