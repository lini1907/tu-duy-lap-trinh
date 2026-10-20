"""Khấu hao đường thẳng theo bài 109, trang 89–90.

Tiền đầu vào là số nguyên VND. Làm tròn mức trích đến đồng,
điều chỉnh kỳ cuối để tổng khấu hao luôn bằng nguyên giá.
Không phụ thuộc PyQt6; bài 130 import trực tiếp module này.
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
import re

MAX_MONEY = 999_999_999_999_999
MAX_YEARS = 100


def parse_money(text: str, label: str = "Số tiền") -> int:
    """Nhận 120000000 hoặc 120.000.000 (dấu chấm phân nhóm nghìn)."""
    text = text.strip()
    if not re.fullmatch(r"(?:[0-9]+|[1-9][0-9]{0,2}(?:\.[0-9]{3})+)", text):
        raise ValueError(f"{label}: nhập số nguyên VND, ví dụ 120000000 hoặc 120.000.000.")
    value = int(text.replace(".", ""))
    if value > MAX_MONEY:
        raise ValueError(f"{label}: tối đa {format_money(MAX_MONEY)} VND.")
    return value


def format_money(value) -> str:
    return f"{int(value):,}".replace(",", ".")


def _validate_money(value, label: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{label} phải là số nguyên VND không âm.")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{label} không hợp lệ.") from None
    if not number.is_finite() or number < 0 or number > MAX_MONEY:
        raise ValueError(f"{label} phải từ 0 đến {format_money(MAX_MONEY)} VND.")
    if number != number.to_integral_value():
        raise ValueError(f"{label} phải là số nguyên VND.")
    return number


@dataclass(frozen=True)
class YearRow:
    year: int
    opening: Decimal
    depreciation: Decimal
    accumulated: Decimal
    remaining: Decimal


@dataclass(frozen=True)
class DepreciationResult:
    original_cost: Decimal
    years: int
    annual: Decimal
    monthly: Decimal
    schedule: tuple[YearRow, ...]


def calculate_depreciation(purchase, transport=0, installation=0,
                           years=1, other=0) -> DepreciationResult:
    """Tính nguyên giá, mức trích năm/tháng và lịch khấu hao từng năm.

    annual/monthly là mức chuẩn đã làm tròn độc lập từ công thức đề bài.
    Nếu làm tròn làm vượt số dư, chỉ trích tối đa số dư hiện có.
    Kỳ cuối trích phần còn lại, vì vậy số dư cuối kỳ luôn bằng 0.
    """
    if isinstance(years, bool) or not isinstance(years, int) or not 1 <= years <= MAX_YEARS:
        raise ValueError(f"Số năm sử dụng phải là số nguyên từ 1 đến {MAX_YEARS}.")
    with localcontext() as ctx:
        ctx.prec = 40
        original = sum((_validate_money(value, label) for value, label in [
            (purchase, "Giá mua"), (transport, "Phí vận chuyển"),
            (installation, "Phí lắp đặt"), (other, "Phí chạy thử / khác"),
        ]), Decimal(0))
        if original <= 0:
            raise ValueError("Nguyên giá phải lớn hơn 0; hãy nhập ít nhất một khoản chi phí.")
        exact_annual = original / years
        annual = exact_annual.quantize(Decimal(1), rounding=ROUND_HALF_UP)
        monthly = (exact_annual / 12).quantize(Decimal(1), rounding=ROUND_HALF_UP)
        remaining = original
        accumulated = Decimal(0)
        rows = []
        for year in range(1, years + 1):
            opening = remaining
            expense = remaining if year == years else min(annual, remaining)
            accumulated += expense
            remaining -= expense
            rows.append(YearRow(year, opening, expense, accumulated, remaining))
        return DepreciationResult(original, years, annual, monthly, tuple(rows))
