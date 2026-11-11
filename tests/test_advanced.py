import math
import unittest
from pfandbriefcalc import (
    cashflow_scenarios,
    project_floating_coupons,
    effective_sensitivities,
    equivalent_cap_rate,
    ship_construction_value_check,
    transport_valuation_review,
    PfandbriefError,
)


class Advanced(unittest.TestCase):
    def test_curve_scenarios_and_sensitivities(self):
        r = cashflow_scenarios([100], [1], [0, 2], [0, 0], method="static")
        self.assertEqual(r.value["BASE"], 100)
        self.assertAlmostEqual(r.value["UP"], 100 * math.exp(-0.025))
        self.assertAlmostEqual(r.value["DOWN"], 100 * math.exp(0.025))
        s = effective_sensitivities([100], [1], [0, 2], [0, 0], bump=0.01).value
        self.assertAlmostEqual(s["effective_duration"], math.sinh(0.01) / 0.01)
        self.assertAlmostEqual(
            s["effective_convexity"], 2 * (math.cosh(0.01) - 1) / 0.01**2
        )

    def test_fixings_projection_and_bound_basis(self):
        args = dict(
            reset_times=[-1, 0.5],
            start_times=[-1, 1],
            end_times=[0, 2],
            accrual_fractions=[1, 1],
            fixings=[0.05, None],
            curve_times=[0, 2],
            zero_rates=[math.log(1.1)] * 2,
            margin=0.02,
            cap=0.11,
        )
        r = project_floating_coupons(**args)
        self.assertAlmostEqual(r.value[0], 0.07)
        self.assertEqual(r.value[1], 0.11)
        args["bound_on"] = "index"
        self.assertAlmostEqual(project_floating_coupons(**args).value[1], 0.12)
        args["fixings"][0] = None
        with self.assertRaisesRegex(PfandbriefError, "MISSING_FIXING"):
            project_floating_coupons(**args)

    def test_equivalence_and_transport_review(self):
        self.assertEqual(equivalent_cap_rate(100, 1000, 0, None, 0.01, 0.2).value, 0.1)
        self.assertAlmostEqual(
            equivalent_cap_rate(
                100, 21000 / 121, 0, 2, 0.01, 0.2, short_life_method="capitalize_land"
            ).value,
            0.1,
            places=9,
        )
        self.assertEqual(
            ship_construction_value_check(90, 90, 100, confirmation_status="MET").value,
            "CHECKS_PASSED",
        )
        self.assertEqual(
            ship_construction_value_check(91, 90, 100, confirmation_status="MET").value,
            "FAILED",
        )
        self.assertEqual(
            ship_construction_value_check(
                90, 90, 100, confirmation_status="MISSING"
            ).value,
            "INCOMPLETE",
        )
        self.assertTrue(
            transport_valuation_review(
                "SCH", "2026-11-11", "2026-01-01", False, 90
            ).value
        )
        self.assertFalse(
            transport_valuation_review(
                "FLG", "2026-11-11", "2026-01-01", False, 89
            ).value
        )


if __name__ == "__main__":
    unittest.main()
