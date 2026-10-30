"""Reproduce WinError 448 by enabling Redirection Guard on this process, then probe PATH handling."""
import ctypes
import os
import shutil
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ProcessRedirectionTrustPolicy = 16
flags = ctypes.c_uint32(1)  # EnforceRedirectionTrust
ok = ctypes.windll.kernel32.SetProcessMitigationPolicy(ProcessRedirectionTrustPolicy, ctypes.byref(flags), 4)
print("redirection guard enabled:", bool(ok))

if "--sanitize" in sys.argv:
    from app.core.pathenv import sanitize_path
    print("dropped:", sanitize_path())

for label, fn in (("shutil.which ffmpeg", lambda: shutil.which("ffmpeg")),
                  ("shutil.which nothing", lambda: shutil.which("nothing-here"))):
    try:
        print(label, "->", fn())
    except OSError as e:
        print(label, "-> OSError", e.winerror)

from app.core.extractor import extract

for u in ("https://www.tiktok.com/@scout2015/video/6718335390845095173",):
    try:
        print("extract ok:", extract(u).title[:30])
    except Exception as e:
        print("extract FAIL:", type(e).__name__, str(e)[:110])
        tb = traceback.extract_tb(e.__traceback__)
        print("  frames:", [(f.filename.replace("\\", "/").split("/")[-1], f.lineno, f.name) for f in tb[-4:]])
