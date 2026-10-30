# PyInstaller spec: onedir, windowed, ffmpeg bundled under bin/
from pathlib import Path

root = Path(SPECPATH).parent

a = Analysis(
    [str(root / "app" / "main.py")],
    pathex=[str(root)],
    datas=[(str(p), "bin") for p in (root / "bin").iterdir() if p.suffix in (".exe", ".dll")],
    hiddenimports=["yt_dlp.compat._legacy", "yt_dlp.compat._deprecated"],
    excludes=["PySide6.QtWebEngineCore", "PySide6.QtQuick", "PySide6.QtQml", "PySide6.Qt3DCore",
              "PySide6.QtMultimedia", "PySide6.QtPdf", "tkinter", "pytest"],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="VideoDownloader", console=False)
coll = COLLECT(exe, a.binaries, a.datas, name="VideoDownloader")
