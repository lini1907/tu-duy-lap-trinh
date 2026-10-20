"""Biểu đồ vector Qt, không cần matplotlib hoặc ảnh bên ngoài."""
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen, QPainterPath
from PyQt6.QtWidgets import QWidget


class BalanceChart(QWidget):
    def __init__(self):
        super().__init__()
        self.result = None
        self.setMinimumHeight(110)
        self.setAccessibleName("Biểu đồ giá trị còn lại theo năm")

    def set_result(self, result):
        self.result = result
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bounds = QRectF(12, 32, self.width() - 24, self.height() - 60)
        painter.setPen(QColor("#64788a"))
        if self.result is None:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "")
            return
        painter.drawText(QPointF(12, 17), "Giá trị còn lại / Nguyên giá")
        painter.drawText(QRectF(self.width() - 155, 0, 143, 25),
                         Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "100% → 0%")
        for ratio in (0, .5, 1):
            y = bounds.bottom() - ratio * bounds.height()
            painter.setPen(QPen(QColor("#e5ecef"), 1))
            painter.drawLine(QPointF(bounds.left(), y), QPointF(bounds.right(), y))
        result = self.result
        values = [result.original_cost] + [row.remaining for row in result.schedule]
        points = [QPointF(bounds.left() + i / result.years * bounds.width(),
                          bounds.bottom() - float(value / result.original_cost) * bounds.height())
                  for i, value in enumerate(values)]
        line = QPainterPath(points[0])
        for point in points[1:]:
            line.lineTo(point)
        painter.setPen(QPen(QColor("#148473"), 2.5))
        painter.drawPath(line)
        painter.setBrush(QColor("#148473"))
        for point in (points[0], points[-1]):
            painter.drawEllipse(point, 4, 4)
        painter.setPen(QColor("#64788a"))
        painter.drawText(QPointF(12, self.height() - 5), "Bắt đầu")
        painter.drawText(QRectF(self.width() - 120, self.height() - 25, 108, 25),
                         Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                         f"Năm {result.years}")
