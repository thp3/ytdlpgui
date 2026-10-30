import sys

from PySide6.QtWidgets import QApplication

from app.core.pathenv import sanitize_path
from app.ui.main_window import MainWindow


def main() -> int:
    sanitize_path()
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
