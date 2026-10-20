"""Chạy từ bất kỳ thư mục nào: python đường_dẫn/ex130/main.py."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    from PyQt6.QtWidgets import QApplication
    from ex130.ui.main_window import DetailedDepreciationWindow
    app = QApplication(sys.argv)
    window = DetailedDepreciationWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
