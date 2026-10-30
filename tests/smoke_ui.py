"""Headless end-to-end check: parse a URL, queue a download, wait for completion."""
import os
import sys
import tempfile
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow, TaskRow

URL = sys.argv[1] if len(sys.argv) > 1 else "https://www.youtube.com/watch?v=jNQXAC9IVRw"


def pump(cond, timeout=120):
    end = time.time() + timeout
    while time.time() < end and not cond():
        app.processEvents()
        time.sleep(0.05)
    return cond()


app = QApplication([])
win = MainWindow()
win.settings.download_dir = tempfile.mkdtemp(prefix="ytdlpgui_")
win.url.setText(URL)
win.parse()
assert pump(lambda: win.info is not None or win.msg.text().startswith("解析失敗")), "parse timeout"
print("parse:", win.info.title if win.info else win.msg.text(), [win.quality.itemText(i) for i in range(win.quality.count())])
assert win.info, win.msg.text()

win.quality.setCurrentIndex(win.quality.count() - 1 if "--audio" in sys.argv else 1)
win.add_task()
row = win.queue.itemWidget(win.queue.item(0))
assert isinstance(row, TaskRow)
assert pump(lambda: row.status.text() in ("完成",) or row.status.text().startswith("失敗")), "download timeout"
print("download:", row.status.text(), row.path)
assert row.status.text() == "完成" and Path(row.path).exists()
print("OK", Path(row.path).stat().st_size, "bytes")
