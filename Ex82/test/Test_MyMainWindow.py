import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
RUNTIME = ROOT / "Ex82" / ".runtime"
if RUNTIME.is_dir():
    sys.path.insert(0, str(RUNTIME))

from PyQt6.QtWidgets import QApplication

from Ex82.ui.MyMainWindowEx import KWhMainWindowEx


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myui = KWhMainWindowEx()
    myui.showWindow()
    sys.exit(app.exec())
