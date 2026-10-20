import unittest
from decimal import Decimal
from ex109.libs.depreciation import calculate_depreciation, parse_money


class DepreciationTests(unittest.TestCase):
    def test_pdf_example(self):
        result = calculate_depreciation(120_000_000, 5_000_000, 1_000_000, 10)
        self.assertEqual(result.original_cost, 126_000_000)
        self.assertEqual(result.annual, 12_600_000)
        self.assertEqual(result.monthly, 1_050_000)
        self.assertEqual([r.remaining for r in result.schedule],
                         [113400000, 100800000, 88200000, 75600000, 63000000,
                          50400000, 37800000, 25200000, 12600000, 0])

    def test_last_period_rounding(self):
        result = calculate_depreciation(100, years=3)
        self.assertEqual([r.depreciation for r in result.schedule], [33, 33, 34])
        result = calculate_depreciation(101, years=3)
        self.assertEqual([r.depreciation for r in result.schedule], [34, 34, 33])

    def test_monthly_not_double_rounded(self):
        self.assertEqual(calculate_depreciation(17, years=3).monthly, 0)

    def test_invariants(self):
        for amount in (1, 2, 49, 50, 99, 100, 101, 123456789, 999999999999999):
            for years in (1, 2, 3, 7, 10, 100):
                with self.subTest(amount=amount, years=years):
                    result = calculate_depreciation(amount, years=years)
                    self.assertEqual(len(result.schedule), years)
                    self.assertEqual(sum(r.depreciation for r in result.schedule), amount)
                    self.assertEqual(result.schedule[-1].remaining, 0)
                    previous = result.original_cost
                    for row in result.schedule:
                        self.assertEqual(row.opening, previous)
                        self.assertGreaterEqual(row.depreciation, 0)
                        self.assertGreaterEqual(row.remaining, 0)
                        self.assertEqual(row.opening - row.depreciation, row.remaining)
                        self.assertEqual(row.remaining + row.accumulated, amount)
                        previous = row.remaining

    def test_other_costs_and_zero_purchase(self):
        self.assertEqual(calculate_depreciation(0, other=120).original_cost, 120)
        self.assertEqual(calculate_depreciation(100, 2, 3, 1, 4).annual, 109)

    def test_invalid_input(self):
        for amount in (-1, "NaN", "Infinity", "abc", True, Decimal("1.1"), 10**15):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                calculate_depreciation(amount)
        with self.assertRaises(ValueError):
            calculate_depreciation(0)
        for years in (0, -1, 101, 1.5, "10", True):
            with self.subTest(years=years), self.assertRaises(ValueError):
                calculate_depreciation(100, years=years)
        with self.assertRaises(ValueError):
            calculate_depreciation(100, transport=-1)

    def test_parse_vnd(self):
        for text in ("120000000", "120.000.000", " 120.000.000 "):
            self.assertEqual(parse_money(text), 120000000)
        for text in ("", "-1", "12.34", "1,000", "1e6", "NaN", "1 000", "0.100"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_money(text)


if __name__ == "__main__":
    unittest.main()
