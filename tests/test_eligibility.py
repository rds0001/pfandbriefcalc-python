import unittest
from pfandbriefcalc import (
    cover_amount,
    mortgage_terms_check,
    transport_loan_check,
    insurance_check,
    required_evidence,
    PfandbriefError,
)


class Eligibility(unittest.TestCase):
    def test_nominal_default_and_rank(self):
        kw = dict(defaulted=True, guaranteed=False, guarantor_defaulted=False)
        self.assertEqual(
            cover_amount(
                "MORTGAGE",
                80,
                75,
                70,
                lien=80,
                lending_value=100,
                prior_claims=10,
                **kw,
            ).value,
            50,
        )
        self.assertEqual(cover_amount("SUBSTITUTE", 80, 75, 70, **kw).value, 0)
        self.assertEqual(
            cover_amount(
                "PUBLIC",
                80,
                75,
                70,
                defaulted=True,
                guaranteed=True,
                guarantor_defaulted=False,
                guarantee_amount=60,
            ).value,
            60,
        )
        self.assertEqual(
            cover_amount(
                "PUBLIC",
                80,
                75,
                70,
                defaulted=False,
                guaranteed=True,
                guarantor_defaulted=True,
                guarantee_amount=60,
            ).value,
            0,
        )

    def test_mortgage_calendar_boundary(self):
        kw = dict(
            permanent_income=True,
            construction_or_land=False,
            right_expiry="2050-02-28",
            economic_end="2041-01-01",
        )
        self.assertEqual(
            mortgage_terms_check("EU_EEA", "2040-02-28", **kw).value, "CHECKS_PASSED"
        )
        self.assertEqual(
            mortgage_terms_check("EU_EEA", "2040-03-01", **kw).value, "FAILED"
        )
        self.assertEqual(
            mortgage_terms_check("OTHER", "2030-01-01", **kw).value, "FAILED"
        )

    def test_transport_balloon_and_exception(self):
        for kind in ("SCH", "FLG"):
            self.assertEqual(
                transport_loan_check(kind, 100, [10] * 8, 20, 18, 25, 2).value,
                "CHECKS_PASSED",
            )
            self.assertEqual(
                transport_loan_check(kind, 100.01, [10] * 8, 20.01, 18, 25, 2).value,
                "FAILED",
            )
            self.assertEqual(
                transport_loan_check(
                    kind, 100, [10] * 8, 20, 18, 25, 5, defer_exception=True
                ).value,
                "CHECKS_PASSED",
            )
            self.assertEqual(
                transport_loan_check(
                    kind, 100, [10] * 8, 20, 18, 25, 5.01, defer_exception=True
                ).value,
                "FAILED",
            )

    def test_insurance_amounts(self):
        for kind in ("SCH", "FLG"):
            r = insurance_check(kind, 130, 100, prior_equal_claims=20)
            self.assertEqual(r.value, "CHECKS_PASSED")
            self.assertEqual(r.details["required"], 130)
            self.assertEqual(
                insurance_check(kind, 129.99, 100, prior_equal_claims=20).value,
                "FAILED",
            )
        self.assertEqual(
            insurance_check(
                "HYP", 60, 100, basis="claim_current_value", current_value_loss=60
            ).value,
            "CHECKS_PASSED",
        )

    def test_required_evidence_not_empty(self):
        r = required_evidence("FLG", "aircraft", "AIRCRAFT", ["foreign", "partial"])
        self.assertIn("engines_reregistration", [x["requirement_id"] for x in r.value])
        self.assertIn("feature_partial", [x["requirement_id"] for x in r.value])
        with self.assertRaisesRegex(PfandbriefError, "KIND_MISMATCH"):
            required_evidence("OEF", "a", "MORTGAGE")


if __name__ == "__main__":
    unittest.main()
