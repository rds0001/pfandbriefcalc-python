import csv
from pathlib import Path
import tempfile
import unittest
from pfandbriefcalc import (
    analyze_pool,
    example_pool,
    pool_metrics,
    aggregate_positions,
    maturity_buckets,
    weighted_ltv,
    reconcile_totals,
    export_table,
    PfandbriefError,
)


class Reporting(unittest.TestCase):
    def test_metric_reconciliation(self):
        result = analyze_pool(**example_pool("HYP", scale=1).value)
        metrics = {r["metric"]: r["value"] for r in pool_metrics(result).value}
        self.assertEqual(metrics["nominal_surplus"], 4)
        self.assertEqual(metrics["nominal_oc_ratio"], 0.04)
        self.assertIsNone(metrics["liquidity_peak_day"])
        self.assertEqual(
            reconcile_totals({"x": metrics["assets_nominal"]}, {"x": 104}).value,
            "CHECKS_PASSED",
        )
        self.assertEqual(reconcile_totals({}, {"x": 0}).value, "INCOMPLETE")
        self.assertEqual(reconcile_totals({"x": 1}, {"x": 2}).value, "FAILED")

    def test_buckets_and_group_totals(self):
        rows = [
            dict(
                position_id="a",
                kind="HYP",
                currency="EUR",
                amount=60,
                date="2026-07-31",
            ),
            dict(
                position_id="b",
                kind="HYP",
                currency="EUR",
                amount=40,
                date="2026-08-01",
            ),
        ]
        result = maturity_buckets(rows, "2026-01-31")
        self.assertEqual(result.value[0]["amount"], 60)
        self.assertEqual(result.value[1]["amount"], 40)
        self.assertEqual(
            aggregate_positions(rows, ["kind", "currency"], "amount").value,
            [dict(kind="HYP", currency="EUR", amount=100)],
        )
        ltvs = [
            dict(
                position_id="a",
                property_id="p1",
                allocated_amount=60,
                used_lien_with_prior_equal=60,
                lending_value=120,
            ),
            dict(
                position_id="b",
                property_id="p2",
                allocated_amount=40,
                used_lien_with_prior_equal=60,
                lending_value=80,
            ),
        ]
        self.assertEqual(weighted_ltv(ltvs).value, 0.60)
        ltvs.append(
            dict(
                position_id="a2",
                property_id="p1",
                allocated_amount=20,
                used_lien_with_prior_equal=60,
                lending_value=100,
            )
        )
        self.assertEqual(weighted_ltv(ltvs).value, 0.70)
        self.assertEqual(weighted_ltv(ltvs).details["ignored_position_ids"], ["a"])

    def test_csv_lossless_text_and_explicit_overwrite(self):
        rows = [dict(id='ä,"quoted"\nline', amount=1.25, missing=None, flag=True)]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "metrics.csv"
            export_table(rows, path)
            with path.open(encoding="utf-8", newline="") as f:
                output = list(csv.DictReader(f))
            self.assertEqual(output[0]["id"], rows[0]["id"])
            self.assertEqual(output[0]["amount"], "1.25")
            self.assertEqual(output[0]["flag"], "true")
            with self.assertRaisesRegex(PfandbriefError, "TARGET_EXISTS"):
                export_table(rows, path)
            export_table(rows, path, overwrite=True)


if __name__ == "__main__":
    unittest.main()
