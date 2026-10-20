"""Xử lý bài 109; giao diện được sinh riêng trong main_window_ui.py."""
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from ex109.libs.depreciation import calculate_depreciation, parse_money, format_money
from ex109.ui.main_window_ui import Ui_MainWindow


class DepreciationWindow(QMainWindow):
    exercise = "109"
    ui_class = Ui_MainWindow

    def __init__(self):
        super().__init__()
        self.result = None
        # Bài 130 chọn lớp giao diện khác, dùng lại toàn bộ xử lý của bài 109.
        self.ui = self.ui_class()
        self.ui.setupUi(self)
        self.fields = {
            "purchase": self.ui.purchaseEdit, "transport": self.ui.transportEdit,
            "installation": self.ui.installationEdit, "other": self.ui.otherEdit,
        }
        self.metrics = [self.ui.originalValue, self.ui.annualValue, self.ui.monthlyValue]
        for editor in self.fields.values():
            editor.textChanged.connect(self.invalidate)
            editor.returnPressed.connect(self.calculate)
        self.ui.years.valueChanged.connect(self.invalidate)
        self.ui.calculate_button.clicked.connect(self.calculate)
        self.ui.sample_button.clicked.connect(self.load_example)
        self.ui.clear_button.clicked.connect(self.reset)
        self.ui.help_button.clicked.connect(self.show_help)
        self.ui.error.hide()
        self.ui.status.hide()
        self.ui.purchaseEdit.setFocus()

    def show_help(self):
        QMessageBox.information(
            self, "Cách tính khấu hao",
            "Nhập số nguyên VND, ví dụ 120000000 hoặc 120.000.000. "
            "Không phát sinh chi phí thì nhập 0. Thời gian sử dụng: 1–100 năm.\n\n"
            "Nguyên giá = Giá mua + Vận chuyển + Lắp đặt + Chi phí khác.\n"
            "Khấu hao năm = Nguyên giá ÷ Số năm.\n"
            "Khấu hao tháng = Khấu hao năm chưa làm tròn ÷ 12.\n\n"
            "Mức trích làm tròn đến đồng; 0,5 làm tròn lên. Năm cuối trích phần "
            "còn lại để số dư bằng 0. Mức tháng là mức tham khảo, không phải "
            "lịch phân bổ từng tháng.\n\n"
            "Enter trong ô tiền hoặc Ctrl+Enter: tính khấu hao.\n"
            "Dữ liệu mẫu: số liệu của đề bài.")

    def invalidate(self):
        self.result = None
        if not hasattr(self, "metrics"):
            return
        for metric in self.metrics:
            metric.setText("—")
        self.ui.error.hide()
        self.ui.status.clear()
        self.ui.status.hide()

    def calculate(self):
        try:
            values = {}
            for key, editor in self.fields.items():
                try:
                    values[key] = parse_money(editor.text(), editor.accessibleName())
                except ValueError:
                    editor.setFocus()
                    raise
            result = calculate_depreciation(**values, years=self.ui.years.value())
        except ValueError as exc:
            self.invalidate()
            self.ui.error.setText(str(exc))
            self.ui.error.show()
            return False
        self.result = result
        for widget, amount in zip(self.metrics, (result.original_cost, result.annual, result.monthly)):
            widget.setText(f"{format_money(amount)} ₫")
        self.ui.error.hide()
        # Kết quả là phản hồi thành công; không lặp lại bằng thông báo.
        self.ui.status.hide()
        return True

    def load_example(self):
        for key, value in dict(purchase="120.000.000", transport="5.000.000",
                               installation="1.000.000", other="0").items():
            self.fields[key].setText(value)
        self.ui.years.setValue(10)
        self.calculate()

    def reset(self):
        for key, editor in self.fields.items():
            editor.setText("" if key == "purchase" else "0")
        self.ui.years.setValue(10)
        self.invalidate()
        self.fields["purchase"].setFocus()
