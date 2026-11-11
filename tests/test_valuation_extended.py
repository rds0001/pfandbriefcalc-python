import unittest
import pfandbriefcalc as p


class PropertyReferences(unittest.TestCase):
    def test_exact_decimal_index_rounding(self):
        self.assertEqual(
            p.indexed_administration_cost("condominium", 53.1, 129.8).value, 113
        )
        self.assertEqual(
            p.indexed_administration_cost("condominium", 53.0999999999999, 129.8).value,
            112,
        )
        with self.assertRaisesRegex(p.PfandbriefError, "INDEX_PRECISION"):
            p.indexed_administration_cost("dwelling", 1.234567890123456, 100)

    def test_costs(self):
        self.assertEqual(p.indexed_administration_cost("dwelling", 130, 100).value, 299)
        self.assertEqual(
            p.indexed_administration_cost("condominium", 130, 100).value, 358
        )
        estimates = dict(
            administration=0, maintenance=0, rent_loss=0, operating=0, modernization=0
        )
        r = p.operating_costs(
            10000, 100000, "commercial", "medium", "none", estimates, 0
        )
        self.assertEqual(r.value, 1500)
        self.assertEqual(r.details["net_income"], 8500)
        estimates["operating"] = 100
        r = p.operating_costs(
            10000, 100000, "commercial", "medium", "medium", estimates, 0
        )
        self.assertEqual(r.value, 2100)
        self.assertEqual(
            p.operating_costs(
                10000, 100000, "commercial", "medium", "none", estimates, 3000
            ).value,
            3000,
        )
        self.assertEqual(p.linear_depreciation(30, 60).value, 0.5)
        self.assertEqual(p.construction_value_limit(20, 100, 80, 0.5, 0).value, 50)
        self.assertEqual(p.foreign_perpetuity_value(100, 0.05, 10, True).value, 1800)

    def test_value_checks(self):
        kwargs = dict(income_estimate=100, deductions_not_already_included=True)
        r = p.property_value_check(95, 110, "income_standard", 70, **kwargs)
        self.assertEqual(r.value, "REVIEW_REQUIRED")
        self.assertEqual(r.details["arithmetic_limit"], 100)
        r = p.property_value_check(
            95, 110, "income_standard", 70, sustainability_review=True, **kwargs
        )
        self.assertEqual(r.value, "CHECKS_PASSED")
        self.assertEqual(
            p.property_value_check(101, 110, "income_standard", 90, **kwargs).value,
            "FAILED",
        )
        r = p.property_value_check(
            90,
            110,
            "owner_comparison",
            100,
            deductions_not_already_included=True,
            property_type="single_family",
            owner_occupation_suitability=True,
            comparable_count=4,
            qualified_model=False,
        )
        self.assertEqual(r.value, "FAILED")
        r = p.valuation_review(
            "2025-02-28", "2024-02-29", False, 90, owner_occupied_residential=True
        )
        self.assertTrue(r.details["monitoring_due"])
        self.assertFalse(r.details["review_required"])
        self.assertTrue(p.valuation_review("2025-01-01", "2024-12-31", False, 90).value)

    def test_parameters_and_simplification(self):
        self.assertEqual(
            p.property_parameter_check("residential", 80, 0.055, 0.055).value,
            "CHECKS_PASSED",
        )
        self.assertEqual(
            p.property_parameter_check("production", 40, 0.065, 0.065).value, "FAILED"
        )
        r = p.property_parameter_check(
            "logistics", 40, 0.065, 0.065, prime_reduction=0.005
        )
        self.assertEqual(r.value, "REVIEW_REQUIRED")
        self.assertTrue(p.small_loan_check(500000, 100000, 1 / 3, True, "full").value)
        self.assertFalse(p.small_loan_check(500001, 100000, 1 / 3, True, "full").value)
        self.assertTrue(
            p.small_loan_check(
                500000,
                0,
                0,
                True,
                "video",
                remaining_life=40,
                video_complete=True,
                video_documented=True,
                valuation_haircut=0.05,
                reason_documented=True,
            ).value
        )
        self.assertFalse(
            p.small_loan_check(
                500000,
                0,
                0,
                True,
                "video",
                remaining_life=39,
                video_complete=True,
                video_documented=True,
                valuation_haircut=0.05,
                reason_documented=True,
            ).value
        )

    def test_rejections(self):
        cases = [
            (lambda: p.linear_depreciation(61, 60), "OUT_OF_RANGE"),
            (
                lambda: p.property_value_check(
                    90,
                    100,
                    "income_standard",
                    80,
                    income_estimate=100,
                    deductions=10,
                    deductions_not_already_included=False,
                ),
                "DOUBLE_DEDUCTION",
            ),
            (
                lambda: p.foreign_perpetuity_value(100, 0.05, 10, False),
                "MISSING_EVIDENCE",
            ),
            (
                lambda: p.property_parameter_check("residential", 80, 0.055, None),
                "INVALID_NUMBER",
            ),
        ]
        for call, code in cases:
            with self.assertRaises(p.PfandbriefError) as e:
                call()
            self.assertEqual(e.exception.code, code)


if __name__ == "__main__":
    unittest.main()
