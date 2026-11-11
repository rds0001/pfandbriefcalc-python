import unittest
from pfandbriefcalc import (
    covered_bond_risk_weight,
    european_label,
    crr_pool_check,
    covered_bond_lcr,
    liquid_buffer_value,
    PfandbriefError,
)


class EU(unittest.TestCase):
    def test_rating_and_labels(self):
        self.assertEqual(
            covered_bond_risk_weight(cqs=3, eligibility_status="MET").value, 0.20
        )
        self.assertEqual(
            covered_bond_risk_weight(
                issuer_risk_weight=0.75, eligibility_status="MET"
            ).value,
            0.35,
        )
        self.assertIsNone(
            covered_bond_risk_weight(cqs=1, eligibility_status="MISSING").value
        )
        self.assertFalse(
            european_label("FLG", "2022-07-08", pfandbrief_status="MET").value[
                "premium"
            ]
        )
        self.assertTrue(
            european_label("SCH", "2022-07-08", pfandbrief_status="MET").value[
                "premium"
            ]
        )
        self.assertFalse(
            european_label("HYP", "2022-07-07", pfandbrief_status="MET").value[
                "premium"
            ]
        )

    def test_crr_limits_and_transition(self):
        rows = [
            dict(
                exposure_id=str(cqs),
                amount=amount,
                cqs=cqs,
                oc_amount=0,
                settlement_amount=0,
                category="LIQUIDITY_DEPOSIT",
                original_days=100,
                approved=False,
            )
            for cqs, amount in ((1, 5), (2, 2), (3, 8))
        ]
        kw = dict(issue_date="2023-01-01", as_of="2026-11-11", eligibility_status="MET")
        self.assertEqual(crr_pool_check(105, 100, rows, **kw).value, "CHECKS_PASSED")
        rows[1]["amount"] = 2.01
        self.assertEqual(crr_pool_check(105, 100, rows, **kw).value, "FAILED")
        rows[1]["oc_amount"] = 0.01
        self.assertEqual(crr_pool_check(105, 100, rows, **kw).value, "CHECKS_PASSED")
        self.assertEqual(
            crr_pool_check(102, 100, [], required_oc=0.02, **kw).value, "INCOMPLETE"
        )
        self.assertEqual(
            crr_pool_check(
                102, 100, [], required_oc=0.02, national_reduction_status="MET", **kw
            ).value,
            "CHECKS_PASSED",
        )
        self.assertEqual(
            crr_pool_check(
                100,
                100,
                [],
                "2022-07-07",
                "2026-11-11",
                eligibility_status="MET",
                legacy_status="MET",
            ).value,
            "CHECKS_PASSED",
        )

    def test_lcr_classes(self):
        conditions = dict(covered_bond_definition=True, bank_exposures=True)
        self.assertEqual(
            covered_bond_lcr(500e6, 0.02, conditions, cqs=1).value, "LEVEL1_COVERED"
        )
        self.assertEqual(
            covered_bond_lcr(250e6, 0.02, conditions, cqs=1).value, "LEVEL2A"
        )
        self.assertEqual(
            covered_bond_lcr(500e6, 0.07, conditions, cqs=2).value, "LEVEL2A"
        )
        self.assertEqual(
            covered_bond_lcr(500e6, 0.02, {}, cqs=1).details["decision"], "INCOMPLETE"
        )
        conditions.update(
            level2b_collateral=True, level2b_underlying_rw=True, monthly_disclosure=True
        )
        self.assertEqual(
            covered_bond_lcr(250e6, 0.10, conditions, cqs=4).value, "LEVEL2B_COVERED"
        )

    def test_haircut_and_calendar(self):
        self.assertAlmostEqual(
            liquid_buffer_value(
                100, "LEVEL1_COVERED", qualification_status="MET"
            ).value,
            93,
        )
        self.assertAlmostEqual(
            liquid_buffer_value(
                100,
                "LEVEL1_COVERED",
                qualification_status="MET",
                additional_fx_haircut=0.1,
            ).value,
            83.7,
        )
        for date, amount in (("2026-04-30", 100), ("2026-05-01", 0)):
            self.assertEqual(
                liquid_buffer_value(
                    100,
                    "BANK_DEPOSIT",
                    qualification_status="MET",
                    as_of="2026-01-31",
                    maturity=date,
                ).value,
                amount,
            )
        with self.assertRaisesRegex(PfandbriefError, "OUT_OF_RANGE"):
            liquid_buffer_value(
                100, "LEVEL2A", qualification_status="MET", haircut=0.10
            )


if __name__ == "__main__":
    unittest.main()
