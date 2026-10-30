"""Manual check: parse + download a Bilibili video through the app's own core with a cookies file.

usage: python tests/manual_bilibili.py <cookies.txt> [url]
"""
import os
import sys
import tempfile
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.downloader import download
from app.core.extractor import extract
from app.core.netopts import NetOptions

cookies = sys.argv[1]
url = sys.argv[2] if len(sys.argv) > 2 else "https://www.bilibili.com/video/av1074402"
net = NetOptions(cookies_file=cookies)
v = extract(url, net)
q = v.qualities[3] if len(v.qualities) > 3 else v.qualities[0]
out = tempfile.mkdtemp(prefix="bili_app_")
p = download(v.url, q.format, out, lambda x: None, threading.Event(), net=net)
print("quality:", q.label, "| file:", os.path.basename(p), os.path.getsize(p), "bytes")
