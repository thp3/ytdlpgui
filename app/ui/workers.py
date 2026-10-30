import threading

from PySide6.QtCore import QObject, QRunnable, Signal

from app.core.downloader import Cancelled, download, friendly_error
from app.core.extractor import extract
from app.core.log import log_exception
from app.core.netopts import NetOptions


class _Signals(QObject):
    done = Signal(object)
    failed = Signal(str)
    progress = Signal(object)


class ExtractWorker(QRunnable):
    def __init__(self, url: str, net: NetOptions):
        super().__init__()
        self.url, self.net = url, net
        self.signals = _Signals()

    def run(self) -> None:
        try:
            self.signals.done.emit(extract(self.url, self.net))
        except Exception as e:  # surfaced to the user
            log_exception(f"extract {self.url}", e)
            self.signals.failed.emit(friendly_error(e))


class DownloadWorker(QRunnable):
    def __init__(self, url: str, fmt: str, outdir: str, net: NetOptions):
        super().__init__()
        self.url, self.fmt, self.outdir, self.net = url, fmt, outdir, net
        self.cancel = threading.Event()
        self.signals = _Signals()

    def run(self) -> None:
        try:
            path = download(self.url, self.fmt, self.outdir, self.signals.progress.emit,
                            self.cancel, net=self.net)
            self.signals.done.emit(path)
        except Cancelled:
            self.signals.failed.emit("已取消")
        except Exception as e:
            log_exception(f"download {self.url}", e)
            self.signals.failed.emit(friendly_error(e))
