"""Xuất CSV UTF-8 BOM để mở được tiếng Việt trong Excel."""
import csv
from ex109.libs.depreciation import DepreciationResult


def export_csv(path, result: DepreciationResult):
    with open(path, "w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(["Năm", "Giá trị đầu năm (VND)", "Khấu hao năm (VND)",
                         "Khấu hao lũy kế (VND)", "Giá trị còn lại (VND)"])
        for row in result.schedule:
            writer.writerow([row.year, int(row.opening), int(row.depreciation),
                             int(row.accumulated), int(row.remaining)])
