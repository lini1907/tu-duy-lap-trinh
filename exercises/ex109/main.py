"""Chạy trực tiếp: python ex109/main.py; hoặc python -m ex109.main."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    from PyQt6.QtWidgets import QApplication
    from ex109.ui.main_window import DepreciationWindow
    app = QApplication(sys.argv)
    window = DepreciationWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
