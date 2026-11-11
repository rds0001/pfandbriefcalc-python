import copy
import unittest
from pfandbriefcalc import (
    example_pool,
    cashflow_example_pool,
    analyze_pool,
    PfandbriefError,
)


class Integration(unittest.TestCase):
    def test_cashflow_derived_pools(self):
        for kind in ("HYP", "OEF", "SCH", "FLG"):
            data = cashflow_example_pool(kind, scale=1)
            result = analyze_pool(**data.value)
            self.assertEqual(result.value, "CHECKS_PASSED")
            self.assertEqual(result.details["liquidity"]["value"], 1)
            self.assertLess(
                data.value["positions"][0]["pv_up"],
                data.value["positions"][0]["pv_base"],
            )
            self.assertGreater(
                data.value["positions"][0]["pv_down"],
                data.value["positions"][0]["pv_base"],
            )

    def test_four_complete_pools_missing_failed_and_immutable(self):
        for kind in ("HYP", "OEF", "SCH", "FLG"):
            args = example_pool(kind, scale=1).value
            original = copy.deepcopy(args)
            result = analyze_pool(**args)
            self.assertEqual(result.value, "CHECKS_PASSED")
            self.assertEqual(
                result.details["coverage"]["details"]["assets_nominal"],
                104 if kind in ("HYP", "OEF") else 107,
            )
            self.assertEqual(
                result.details["coverage"]["details"]["nominal_headroom"], 0
            )
            self.assertEqual(args, original)
            args["evidence"] = []
            result = analyze_pool(**args)
            self.assertEqual(result.value, "INCOMPLETE")
            self.assertTrue(result.details["arithmetic_pass"])
            args = original
            args["evidence"][0]["conclusion"] = "NOT_MET"
            result = analyze_pool(**args)
            self.assertEqual(result.value, "FAILED")
            self.assertEqual(
                result.details["coverage"]["details"]["assets_nominal"],
                4 if kind in ("HYP", "OEF") else 7,
            )

    def test_negative_derivative_never_disappears(self):
        args = example_pool("HYP", scale=1).value
        derivative = dict(
            position_id="hedge",
            kind="HYP",
            category="DERIVATIVE",
            currency="EUR",
            amounts={},
            pv_base=-10,
            pv_up=-20,
            pv_down=5,
            features=[],
            limits=dict(
                tier="T3",
                bank_group="counterparty",
                construction=False,
                land=False,
                foreign_bucket="OTHER_PROTECTED",
                downgraded=False,
                liquidity_only=False,
                pv_oc_exempt=False,
                pure_fx_hedge=False,
            ),
        )
        args["positions"].append(derivative)
        args["cashflows"] = [
            dict(
                flow_id="d", position_id="hedge", date="2026-11-12", inflow=0, outflow=3
            )
        ]
        result = analyze_pool(**args)
        self.assertEqual(result.value, "FAILED")
        self.assertEqual(
            result.details["coverage"]["details"]["liabilities_nominal"], 110
        )
        self.assertEqual(result.details["stress"]["value"], 16)
        self.assertEqual(result.details["liquidity"]["value"], 3)

    def test_own_bond_requires_evidence_and_unknown_flows_fail(self):
        args = example_pool("OEF", scale=1).value
        args["positions"][-1]["amounts"]["own_held_excluded"] = True
        result = analyze_pool(**args)
        self.assertEqual(result.value, "INCOMPLETE")
        self.assertEqual(
            result.details["coverage"]["details"]["liabilities_nominal"], 100
        )
        args["cashflows"] = [
            dict(
                flow_id="bad",
                position_id="missing",
                date="2026-11-12",
                inflow=10,
                outflow=0,
            )
        ]
        with self.assertRaisesRegex(PfandbriefError, "UNKNOWN_KEY"):
            analyze_pool(**args)


if __name__ == "__main__":
    unittest.main()
