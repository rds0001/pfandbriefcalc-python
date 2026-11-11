import math
import unittest
import pfandbriefcalc as p


class FinanceReferences(unittest.TestCase):
    def test_dates_and_schedule(self):
        self.assertAlmostEqual(
            p.year_fraction("2024-02-28", "2024-03-01", "ACT/365F").value, 2 / 365
        )
        self.assertAlmostEqual(
            p.year_fraction("2024-02-28", "2024-03-01", "ACT/ACT-ISDA").value, 2 / 366
        )
        self.assertAlmostEqual(
            p.year_fraction("2025-01-31", "2025-02-28", "30E/360").value, 28 / 360
        )
        self.assertEqual(
            p.adjust_date("2025-08-31", "following", []).value, "2025-09-01"
        )
        self.assertEqual(
            p.adjust_date("2025-08-31", "modified_following", []).value, "2025-08-29"
        )
        s = p.coupon_schedule(
            "2025-01-01", "2027-01-01", 1, "30E/360", "unadjusted", []
        ).value
        r = p.contract_cashflows(s, 100, [0.1, 0.1], [0, 0]).value
        self.assertEqual([x["amount"] for x in r], [10, 110])
        r = p.contract_cashflows(s, 100, [0.1, 0.1], [40, 0]).value
        self.assertEqual([x["amount"] for x in r], [50, 66])
        s = p.coupon_schedule(
            "2024-12-15",
            "2025-05-31",
            4,
            "ACT/365F",
            "unadjusted",
            [],
            end_of_month=True,
        ).value
        self.assertEqual([x["end"] for x in s], ["2025-02-28", "2025-05-31"])

    def test_valuation(self):
        self.assertAlmostEqual(
            p.present_value([110], [1], [1], [math.log(1.1)]).value, 100, places=11
        )
        self.assertAlmostEqual(
            p.discount_factors([2], [1, 3], [0, 0.04]).value[0],
            math.exp(-0.04),
            places=14,
        )
        r = p.bond_analytics([110], [1], 0.1, 1, accrued_interest=2)
        self.assertAlmostEqual(r.value, 100, places=11)
        self.assertAlmostEqual(r.details["clean_price"], 98, places=11)
        self.assertEqual(r.details["macaulay_duration"], 1)
        self.assertAlmostEqual(r.details["modified_duration"], 10 / 11, places=12)
        self.assertAlmostEqual(r.details["convexity"], 200 / 121, places=12)
        self.assertAlmostEqual(
            p.bond_analytics([10, 110], [1, 2], 0.1, 1).value, 100, places=11
        )
        self.assertAlmostEqual(
            p.yield_to_maturity(100, [10, 110], [1, 2], 1, -0.1, 0.5).value,
            0.1,
            places=11,
        )
        self.assertAlmostEqual(
            p.accrued_interest(
                100, 0.1, "2025-01-01", "2025-07-01", "2026-01-01", "30E/360"
            ).value,
            5,
        )

    def test_stresses(self):
        tenors = [1 / 12, 1, 2, 5, 7, 10, 15]
        static = p.rate_shocks([0.01], method="static")
        self.assertAlmostEqual(static.details["down"][0], -0.015)
        self.assertAlmostEqual(static.details["up"][0], 0.035)
        r = p.rate_shocks(
            [0.02] * 7,
            method="dynamic",
            tenors=tenors,
            history=[[0.02] * 7 for _ in range(250)],
        )
        self.assertEqual(r.value, [0.01] * 7)
        factor = math.sqrt(250 / 249) * 2.33 * math.sqrt(125)
        history = [[0.02 if i % 2 == 0 else 0.04] * 7 for i in range(250)]
        r = p.rate_shocks([0.02] * 7, method="dynamic", tenors=tenors, history=history)
        self.assertEqual(r.details["mode"], "log_changes")
        self.assertAlmostEqual(r.value[1], 0.02 * math.log(2) * factor, places=12)
        for row in history:
            row[0] = -0.01
        r = p.rate_shocks([0.02] * 7, method="dynamic", tenors=tenors, history=history)
        self.assertEqual(r.details["mode"], "absolute_changes")
        self.assertAlmostEqual(r.value[1], 0.02 * factor, places=12)
        self.assertEqual(r.value[0], 0.01)
        self.assertEqual(p.fx_shock(method="dynamic", history=[1] * 250).value, 0)
        r = p.fx_shock(
            method="dynamic",
            history=[1 if i % 2 == 0 else math.exp(0.01) for i in range(250)],
        )
        self.assertAlmostEqual(r.value, 0.01 * factor, places=12)
        self.assertEqual(p.stressed_fx_net(100, 0.9, 0.2).value, 72)
        self.assertEqual(p.stressed_fx_net(-100, 0.9, 0.2).value, -108)

    def test_rejections(self):
        cases = [
            (lambda: p.discount_factors([2], [1], [0.02]), "CURVE_RANGE"),
            (lambda: p.yield_to_maturity(100, [110], [1], 1, 0.2, 0.5), "NO_BRACKET"),
            (lambda: p.bond_analytics([-1, 110], [1, 2], 0.1, 1), "OUT_OF_RANGE"),
            (
                lambda: p.rate_shocks([0.01], method="dynamic", tenors=[1], history=[]),
                "MISSING_TENOR",
            ),
            (lambda: p.stressed_fx_net(1, 1, 1.1), "INVALID_STRESS"),
            (
                lambda: p.year_fraction("2025-02-30", "2025-03-01", "ACT/360"),
                "INVALID_DATE",
            ),
            (
                lambda: p.fx_shock(method="static", currency_group="OTHER"),
                "INVALID_NUMBER",
            ),
            (
                lambda: p.present_value([1e308, 1e308], [0, 0], [1], [0]),
                "NUMERIC_RANGE",
            ),
        ]
        for call, code in cases:
            with self.assertRaises(p.PfandbriefError) as e:
                call()
            self.assertEqual(e.exception.code, code)


if __name__ == "__main__":
    unittest.main()
