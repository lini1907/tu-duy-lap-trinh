import csv
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from ex109.libs.depreciation import calculate_depreciation
from ex109.ui.main_window import DepreciationWindow
from ex130.ui.main_window import DetailedDepreciationWindow
from ex130.libs.export import export_csv

APP = QApplication.instance() or QApplication([])


class GuiTests(unittest.TestCase):
    def setUp(self):
        self.window = DetailedDepreciationWindow()

    def tearDown(self):
        self.window.close()

    def test_reuse(self):
        self.assertIsInstance(self.window, DepreciationWindow)
        self.window.load_example()
        self.assertEqual(self.window.result, calculate_depreciation(120000000, 5000000, 1000000, 10))

    def test_both_windows_run_without_loading_ui_xml(self):
        # Khi chạy ứng dụng chỉ dùng Python đã sinh, không đọc lại .ui.
        with patch("PyQt6.uic.loadUi", side_effect=AssertionError("Unexpected XML load")):
            for window_class in (DepreciationWindow, DetailedDepreciationWindow):
                with self.subTest(window=window_class.__name__):
                    window = window_class()
                    try:
                        QTest.mouseClick(window.ui.sample_button, Qt.MouseButton.LeftButton)
                        self.assertEqual(window.metrics[0].text(), "126.000.000 ₫")
                        self.assertEqual(window.metrics[1].text(), "12.600.000 ₫")
                        self.assertEqual(window.metrics[2].text(), "1.050.000 ₫")
                        QTest.mouseClick(window.ui.clear_button, Qt.MouseButton.LeftButton)
                        self.assertIsNone(window.result)
                    finally:
                        window.close()

    def test_buttons_details_and_stale_data(self):
        QTest.mouseClick(self.window.ui.sample_button, Qt.MouseButton.LeftButton)
        self.assertEqual(self.window.metrics[0].text(), "126.000.000 ₫")
        self.assertEqual(self.window.ui.table.rowCount(), 0)
        QTest.mouseClick(self.window.ui.detail_button, Qt.MouseButton.LeftButton)
        self.assertEqual(self.window.ui.tabs.currentIndex(), 1)
        self.assertEqual(self.window.ui.table.rowCount(), 10)
        self.assertEqual(self.window.ui.table.item(9, 4).text(), "0")
        self.assertTrue(self.window.ui.export_button.isEnabled())
        self.window.fields["purchase"].setText("100")
        self.assertIsNone(self.window.result)
        self.assertEqual(self.window.ui.table.rowCount(), 0)
        self.assertFalse(self.window.ui.export_button.isEnabled())
        self.assertEqual(self.window.metrics[0].text(), "—")

    def test_invalid_and_reset(self):
        self.window.load_example()
        self.window.fields["purchase"].setText("-1")
        self.window.show_details()
        self.assertFalse(self.window.ui.error.isHidden())
        self.assertIsNone(self.window.result)
        self.assertEqual(self.window.ui.table.rowCount(), 0)
        self.window.reset()
        self.assertEqual(self.window.fields["purchase"].text(), "")
        self.assertEqual(self.window.fields["transport"].text(), "0")
        self.assertTrue(self.window.ui.error.isHidden())

    def test_details_before_calculation(self):
        self.window.fields["purchase"].setText("100")
        self.window.ui.years.setValue(3)
        self.window.show_details()
        self.assertEqual(self.window.ui.table.item(2, 2).text(), "34")
        self.assertEqual(self.window.ui.table.item(2, 4).text(), "0")

    def test_csv(self):
        result = calculate_depreciation(100, years=3)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "report.csv"
            export_csv(path, result)
            self.assertTrue(path.read_bytes().startswith(b"\xef\xbb\xbf"))
            with path.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.reader(stream))
            self.assertEqual(rows[0][0], "Năm")
            self.assertEqual(rows[-1], ["3", "34", "34", "100", "0"])


if __name__ == "__main__":
    unittest.main()
