"""Xử lý bài 130: dùng UI đã sinh và kế thừa chức năng bài 109."""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QTableWidgetItem, QHeaderView, QFileDialog
from ex109.libs.depreciation import format_money
from ex109.ui.main_window import DepreciationWindow
from ex130.ui.chart import BalanceChart
from ex130.libs.export import export_csv
from ex130.ui.main_window_ui import Ui_MainWindow


class DetailedDepreciationWindow(DepreciationWindow):
    exercise = "130"
    ui_class = Ui_MainWindow

    def __init__(self):
        super().__init__()
        self.ui.detail_button.clicked.connect(self.show_details)
        self.ui.export_button.clicked.connect(self.save_csv)
        # QWidget chuẩn trong Designer; không yêu cầu custom-widget plugin.
        self.chart = BalanceChart()
        self.ui.chartLayout.addWidget(self.chart)
        self.chart.hide()
        self.ui.table.horizontalHeader().setMinimumSectionSize(155)
        self.ui.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ui.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.ui.table.horizontalHeader().setMinimumSectionSize(40)
        self.ui.table.verticalHeader().hide()

    def clear_details(self):
        if hasattr(self, "chart"):
            self.ui.table.setRowCount(0)
            self.chart.set_result(None)
            self.chart.hide()
            self.ui.chartPlaceholder.show()
            self.ui.export_button.setEnabled(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resize_columns()

    def resize_columns(self):
        if not hasattr(self, "ui") or self.result is None:
            return
        minimum = max(155, self.ui.table.fontMetrics().horizontalAdvance(
            format_money(self.result.original_cost)) + 30)
        for column in range(1, 5):
            self.ui.table.horizontalHeader().setSectionResizeMode(
                column, QHeaderView.ResizeMode.Interactive)
            self.ui.table.setColumnWidth(
                column, max(minimum, (self.ui.table.viewport().width() - 48) // 4))

    def invalidate(self):
        super().invalidate()
        self.clear_details()

    def calculate(self):
        self.clear_details()
        return super().calculate()

    def show_details(self):
        # Cho phép nhấn nút 2 trước nút 1; luôn kiểm tra lại dữ liệu hiện tại.
        if not self.calculate():
            return
        self.ui.table.setRowCount(len(self.result.schedule))
        for index, row in enumerate(self.result.schedule):
            values = [str(row.year), format_money(row.opening),
                      format_money(row.depreciation), format_money(row.accumulated),
                      format_money(row.remaining)]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter |
                                      (Qt.AlignmentFlag.AlignCenter if column == 0
                                       else Qt.AlignmentFlag.AlignRight))
                if index == self.result.years - 1:
                    item.setBackground(QColor("#dff2e9"))
                    item.setForeground(QColor("#0a6757"))
                self.ui.table.setItem(index, column, item)
            self.ui.table.setRowHeight(index, 36)
        self.chart.set_result(self.result)
        self.ui.chartPlaceholder.hide()
        self.chart.show()
        self.ui.export_button.setEnabled(True)
        self.ui.tabs.setCurrentIndex(1)
        self.resize_columns()

    def save_csv(self):
        if self.result is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Lưu lịch khấu hao", "lich_khau_hao.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            export_csv(path, self.result)
        except OSError as exc:
            self.ui.error.setText(f"Không lưu được tệp: {exc}")
            self.ui.error.show()
            return
        self.ui.error.hide()
        self.ui.status.setText(f"Đã xuất báo cáo: {path}")
        self.ui.status.show()
