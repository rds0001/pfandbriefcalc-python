"""Independent analytic references specified before implementation in STARTKERN."""

import math
import unittest
import pfandbriefcalc as p


class EarlyReferences(unittest.TestCase):
    def test_extreme_number_rejected(self):
        with self.assertRaises(p.PfandbriefError) as caught:
            p.annuity_factor(10**1000, 2)
        self.assertEqual(caught.exception.code, "INVALID_NUMBER")

    def close(self, actual, expected):
        self.assertTrue(
            math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-8),
            (actual, expected),
        )

    def test_valuation_oracles(self):
        self.close(p.annuity_factor(0.1, 2).value, 210 / 121)
        self.close(p.annuity_factor(0, 7).value, 7)
        self.close(
            p.income_value(100, 200, 0.1, 2, short_life_method="capitalize_land").value,
            21000 / 121,
        )
        self.close(
            p.income_value(
                10, 200, 0.1, 2, demolition_costs=20, land_release_years=2
            ).value,
            18000 / 121,
        )
        self.close(p.comparison_value(100000).value, 90000)
        self.close(p.cost_value(100000, 20000, 0.25, incidental_rate=0.2).value, 101000)
        for years, expected in [(10, 90), (5, 85), (3, 75)]:
            self.close(p.ship_value_limit(100, 90, 110, years).value, expected)
        self.close(p.ship_value_limit(None, 90, 110, 10).value, 82.5)
        self.close(p.aircraft_value_limit(100, 95, 110, 10).value, 95)
        self.close(p.aircraft_value_limit(100, None, 110, 0).value, 99)
        self.close(p.aircraft_value_limit(None, 95, 110, 10).value, 82.5)

    def test_coverage_oracles(self):
        self.close(p.secured_amount(80, 100, 100, 20, 100, 0.6).value, 40)
        self.close(p.coverage_amounts(103, 100, 0.02).value, 1)
        self.assertIsNone(p.coverage_amounts(0, 0, 0.02).details["ratio"])
        r = p.liquidity_gap([0, 100], [50, 0], 40)
        self.close(r.value, 50)
        self.assertEqual(r.details["cumulative"], [-50, 50])
        self.assertFalse(r.details["arithmetic_pass"])

    def test_invalid(self):
        cases = [
            (lambda: p.annuity_factor(True, 3), "INVALID_NUMBER"),
            (lambda: p.annuity_factor(float("nan"), 3), "INVALID_NUMBER"),
            (lambda: p.annuity_factor(0.1, -1), "OUT_OF_RANGE"),
            (lambda: p.income_value(100, 200, 0.1, 2), "MISSING_METHOD"),
            (lambda: p.income_value(0, 200, 0.1, 2), "MISSING_INPUT"),
            (lambda: p.liquidity_gap([1], [1, 2], 1), "LENGTH_MISMATCH"),
            (lambda: p.ship_value_limit(1, None, 1, 5), "INCONSISTENT_INPUT"),
        ]
        for call, code in cases:
            with self.assertRaises(p.PfandbriefError) as caught:
                call()
            self.assertEqual(caught.exception.code, code)


if __name__ == "__main__":
    unittest.main()
