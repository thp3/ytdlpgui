import os
import subprocess

from PySide6.QtCore import QThreadPool, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QComboBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget,
                               QListWidgetItem, QMainWindow, QProgressBar, QPushButton,
                               QVBoxLayout, QWidget)

from app.core.extractor import VideoInfo
from app.core.netopts import NetOptions
from app.core.settings import Settings
from .workers import DownloadWorker, ExtractWorker


def fmt_duration(s: int) -> str:
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"


class TaskRow(QWidget):
    def __init__(self, title: str, worker: DownloadWorker):
        super().__init__()
        self.worker, self.path = worker, ""
        self.title = QLabel(title)
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.status = QLabel("等待中")
        self.btn = QPushButton("取消")
        self.btn.clicked.connect(self._on_btn)
        top = QHBoxLayout()
        top.addWidget(self.title, 1)
        top.addWidget(self.btn)
        lay = QVBoxLayout(self)
        lay.addLayout(top)
        lay.addWidget(self.bar)
        lay.addWidget(self.status)
        worker.signals.progress.connect(self._progress)
        worker.signals.done.connect(self._done)
        worker.signals.failed.connect(self._failed)

    def _progress(self, p) -> None:
        self.bar.setValue(int(p.percent))
        self.status.setText(f"{p.status}  {p.speed}  剩餘 {p.eta}".strip())

    def _done(self, path: str) -> None:
        self.path = path
        self.bar.setValue(100)
        self.status.setText("完成")
        self.btn.setText("開啟位置")

    def _failed(self, msg: str) -> None:
        self.status.setText(f"失敗：{msg}")
        self.btn.setEnabled(False)

    def _on_btn(self) -> None:
        if self.path:
            subprocess.Popen(["explorer", "/select,", os.path.normpath(self.path)])
        else:
            self.worker.cancel.set()
            self.btn.setEnabled(False)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("萬用影片下載器")
        self.resize(760, 640)
        self.settings = Settings.load()
        self.pool = QThreadPool()
        self.pool.setMaxThreadCount(self.settings.max_parallel + 2)
        self.info: VideoInfo | None = None

        self.url = QLineEdit()
        self.url.setPlaceholderText("貼上 YouTube / TikTok / Bilibili 網址")
        self.url.returnPressed.connect(self.parse)
        self.parse_btn = QPushButton("解析")
        self.parse_btn.clicked.connect(self.parse)
        self.paste_btn = QPushButton("貼上")
        self.paste_btn.clicked.connect(lambda: self.url.setText(QGuiApplication.clipboard().text().strip()))

        self.card_title = QLabel("")
        self.card_title.setWordWrap(True)
        self.card_title.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.card_meta = QLabel("")
        self.quality = QComboBox()
        self.add_btn = QPushButton("加入下載")
        self.add_btn.setEnabled(False)
        self.add_btn.clicked.connect(self.add_task)

        self.dir_label = QLabel(self.settings.download_dir)
        dir_btn = QPushButton("選擇資料夾")
        dir_btn.clicked.connect(self.choose_dir)
        self.cookies = QComboBox()
        self.cookies.addItems(["不使用 cookies", "chrome", "edge", "firefox"])
        self.cookies.setCurrentText(self.settings.cookies_browser or "不使用 cookies")

        self.cookies_file_label = QLabel(self.settings.cookies_file or "未選擇 cookies.txt")
        cf_btn = QPushButton("選擇 cookies.txt")
        cf_btn.clicked.connect(self.choose_cookies_file)
        cf_clear = QPushButton("清除")
        cf_clear.clicked.connect(self.clear_cookies_file)
        self.proxy = QLineEdit(self.settings.proxy)
        self.proxy.setPlaceholderText("代理（選填），例如 http://127.0.0.1:7890 或 socks5://127.0.0.1:1080")
        self.proxy.editingFinished.connect(self.save_proxy)

        self.queue = QListWidget()
        self.msg = QLabel("")

        row1 = QHBoxLayout()
        row1.addWidget(self.url, 1)
        row1.addWidget(self.paste_btn)
        row1.addWidget(self.parse_btn)
        row2 = QHBoxLayout()
        row2.addWidget(self.quality, 1)
        row2.addWidget(self.add_btn)
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("儲存到："))
        row3.addWidget(self.dir_label, 1)
        row3.addWidget(dir_btn)
        row3.addWidget(self.cookies)

        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Cookies："))
        row4.addWidget(self.cookies_file_label, 1)
        row4.addWidget(cf_btn)
        row4.addWidget(cf_clear)

        root = QWidget()
        lay = QVBoxLayout(root)
        lay.addLayout(row1)
        lay.addWidget(self.card_title)
        lay.addWidget(self.card_meta)
        lay.addLayout(row2)
        lay.addLayout(row3)
        lay.addLayout(row4)
        lay.addWidget(self.proxy)
        lay.addWidget(self.msg)
        lay.addWidget(self.queue, 1)
        self.setCentralWidget(root)

    def cookies_browser(self) -> str:
        t = self.cookies.currentText()
        return t if t in ("chrome", "edge", "firefox") else ""

    def net_options(self) -> NetOptions:
        return NetOptions(self.settings.cookies_file, self.cookies_browser(), self.proxy.text().strip())

    def choose_cookies_file(self) -> None:
        f, _ = QFileDialog.getOpenFileName(self, "選擇 cookies.txt", "", "Cookies (*.txt);;All files (*)")
        if f:
            self.settings.cookies_file = f
            self.cookies_file_label.setText(f)
            self.settings.save()

    def clear_cookies_file(self) -> None:
        self.settings.cookies_file = ""
        self.cookies_file_label.setText("未選擇 cookies.txt")
        self.settings.save()

    def save_proxy(self) -> None:
        self.settings.proxy = self.proxy.text().strip()
        self.settings.save()

    def choose_dir(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "選擇儲存資料夾", self.settings.download_dir)
        if d:
            self.settings.download_dir = d
            self.dir_label.setText(d)
            self.settings.save()

    def parse(self) -> None:
        url = self.url.text().strip()
        if not url:
            return
        self.parse_btn.setEnabled(False)
        self.add_btn.setEnabled(False)
        self.msg.setText("解析中…")
        w = ExtractWorker(url, self.net_options())
        w.signals.done.connect(self._parsed)
        w.signals.failed.connect(self._parse_failed)
        self.pool.start(w)

    def _parsed(self, info: VideoInfo) -> None:
        self.info = info
        self.parse_btn.setEnabled(True)
        self.msg.setText("")
        self.card_title.setText(info.title)
        if info.is_playlist:
            self.card_meta.setText(f"{info.extractor}  播放清單，共 {len(info.entries)} 部")
        else:
            self.card_meta.setText(f"{info.extractor}  {info.uploader}  {fmt_duration(info.duration)}")
        self.quality.clear()
        for q in info.qualities:
            self.quality.addItem(q.label, q.format)
        self.add_btn.setEnabled(True)

    def _parse_failed(self, msg: str) -> None:
        self.parse_btn.setEnabled(True)
        self.msg.setText(f"解析失敗：{msg}")

    def add_task(self) -> None:
        if not self.info:
            return
        fmt = self.quality.currentData()
        targets = self.info.entries if self.info.is_playlist else [self.info]
        for t in targets:
            self._enqueue(t.title, t.url, fmt)
        self.settings.cookies_browser = self.cookies_browser()
        self.settings.save()

    def _enqueue(self, title: str, url: str, fmt: str) -> None:
        w = DownloadWorker(url, fmt, self.settings.download_dir, self.net_options())
        row = TaskRow(title, w)
        item = QListWidgetItem()
        item.setSizeHint(row.sizeHint())
        self.queue.addItem(item)
        self.queue.setItemWidget(item, row)
        self.pool.start(w)
