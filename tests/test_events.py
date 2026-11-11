import unittest
from pfandbriefcalc import (
    validate_register_entries,
    deferred_interest,
    interest_extension,
    extension_plan,
    PfandbriefError,
)


class Events(unittest.TestCase):
    def test_register_number_and_date_not_reused_or_backdated(self):
        entry = dict(
            entry_id="entry",
            kind="HYP",
            register_id="main",
            number=8,
            entry_date="2026-11-11",
            recorded_date="2026-11-11",
            category="MORTGAGE",
            features=[],
            fields=dict(
                file_ref="file",
                object_ref="land-register-reference",
                lending_value=100,
                lien_ref="lien-reference",
                lien_currency="EUR",
                lien_nominal=60,
            ),
        )
        previous = [dict(kind="HYP", register_id="main", number=7)]
        self.assertEqual(
            validate_register_entries([entry], previous).value, "CHECKS_PASSED"
        )
        entry["number"] = 7
        self.assertEqual(validate_register_entries([entry], previous).value, "FAILED")
        entry["number"] = 8
        entry["entry_date"] = "2026-11-10"
        self.assertEqual(validate_register_entries([entry], previous).value, "FAILED")
        entry["entry_date"] = "2026-11-11"
        entry["fields"].pop("object_ref")
        self.assertEqual(
            validate_register_entries([entry], previous).value, "INCOMPLETE"
        )

    def test_extension_preserves_repayment_order(self):
        issues = [
            dict(
                issue_id="early",
                kind="HYP",
                original_date="2026-02-01",
                new_date="2026-08-01",
                principal=100,
                shifted_fraction=1,
                coupon_rate=0.10,
                day_count="ACT/365F",
            ),
            dict(
                issue_id="late",
                kind="HYP",
                original_date="2026-04-01",
                new_date="2026-07-01",
                principal=50,
                shifted_fraction=1,
                coupon_rate=0.10,
                day_count="ACT/365F",
            ),
        ]
        kwargs = dict(
            authority_status="MET", conditions_status="MET", complete_scope_status="MET"
        )
        self.assertEqual(
            extension_plan("HYP", issues, "2026-01-01", "2026-01-02", **kwargs).value,
            "FAILED",
        )
        issues[1]["new_date"] = "2026-08-01"
        r = extension_plan("HYP", issues, "2026-01-01", "2026-01-02", **kwargs)
        self.assertEqual(r.value, "CHECKS_PASSED")
        self.assertFalse(r.details["conditions_presumed"])
        kwargs["conditions_status"] = "MISSING"
        self.assertEqual(
            extension_plan("HYP", issues, "2026-01-01", "2026-01-02", **kwargs).value,
            "INCOMPLETE",
        )

    def test_deferred_accrual_and_first_month(self):
        self.assertEqual(
            deferred_interest(100, 0.1, "2026-01-01", "2027-01-01", "ACT/365F").value,
            10,
        )
        r = interest_extension(
            100,
            0.1,
            "2026-02-10",
            "2026-01-31",
            "2026-02-01",
            "ACT/365F",
            authority_status="MET",
        )
        self.assertEqual(r.value["date"], "2026-02-28")
        self.assertAlmostEqual(r.value["additional_interest"], 180 / 365)
        with self.assertRaisesRegex(PfandbriefError, "INVALID_EXTENSION_DATE"):
            interest_extension(
                100,
                0.1,
                "2026-03-01",
                "2026-01-31",
                "2026-02-01",
                "ACT/365F",
                authority_status="MET",
            )


if __name__ == "__main__":
    unittest.main()
