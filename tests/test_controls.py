from copy import deepcopy
import unittest
import pfandbriefcalc as p


class ControlReferences(unittest.TestCase):
    def test_profiles(self):
        a = dict(
            profile_id="synthetic",
            revision="A",
            valid_from="2025-01-01",
            valid_to="2025-12-31",
            known_from="2024-12-01",
            status="VERIFIED",
            source_ref="synthetic reference",
            parameters={"oc": 0.02},
        )
        b = dict(a, revision="B", known_from="2025-06-01", parameters={"oc": 0.03})
        self.assertEqual(
            p.select_rule_profile(
                [a, b], "synthetic", "2025-03-31", "2025-04-01"
            ).value,
            {"oc": 0.02},
        )
        self.assertEqual(
            p.select_rule_profile(
                [a, b], "synthetic", "2025-03-31", "2025-07-01"
            ).value,
            {"oc": 0.03},
        )
        b["valid_from"] = "2025-07-01"
        with self.assertRaises(p.PfandbriefError) as e:
            p.select_rule_profile([a, b], "synthetic", "2025-03-31", "2025-07-01")
        self.assertEqual(e.exception.code, "PROFILE_DATE")
        a["status"] = "EXPERIMENTAL"
        with self.assertRaises(p.PfandbriefError) as e:
            p.select_rule_profile([a], "synthetic", "2025-03-31", "2025-04-01")
        self.assertEqual(e.exception.code, "UNVERIFIED_PROFILE")

    def test_evidence(self):
        req = [
            dict(
                requirement_id="appraisal",
                scope="asset1",
                allow_not_applicable=False,
                source_ref="synthetic",
            )
        ]
        e = dict(
            evidence_id="e1",
            requirement_id="appraisal",
            scope="asset1",
            valid_from="2025-01-01",
            valid_to="2025-12-31",
            known_from="2025-01-01",
            conclusion="MET",
            reviewer="reviewer",
            source_ref="local report",
            reason="independent synthetic appraisal",
        )
        self.assertEqual(
            p.assess_evidence(req, [], "2025-03-31", "2025-03-31").value, "INCOMPLETE"
        )
        self.assertEqual(
            p.assess_evidence(req, [e], "2025-03-31", "2025-03-31").value,
            "CHECKS_PASSED",
        )
        r = p.assess_evidence(req, [e], "2026-01-01", "2026-01-01")
        self.assertEqual(r.details["checks"][0]["status"], "EXPIRED")
        correction = dict(e, known_from="2025-06-01", conclusion="NOT_MET")
        self.assertEqual(
            p.assess_evidence(req, [e, correction], "2025-03-31", "2025-04-01").value,
            "CHECKS_PASSED",
        )
        self.assertEqual(
            p.assess_evidence(req, [e, correction], "2025-03-31", "2025-07-01").value,
            "FAILED",
        )
        contradictory = dict(correction, evidence_id="e2", known_from="2025-01-01")
        with self.assertRaises(p.PfandbriefError) as err:
            p.assess_evidence(req, [e, contradictory], "2025-03-31", "2025-03-31")
        self.assertEqual(err.exception.code, "CONFLICTING_EVIDENCE")

    def test_allocation(self):
        claims = [
            dict(claim_id="c1", capacity=60, currency="EUR", kind="HYP"),
            dict(claim_id="c2", capacity=50, currency="EUR", kind="HYP"),
        ]
        collateral = [
            dict(collateral_id="k1", capacity=100, currency="EUR", kind="HYP")
        ]
        allocations = [
            dict(
                allocation_id="a1",
                claim_id="c1",
                collateral_id="k1",
                kind="HYP",
                currency="EUR",
                amount=60,
            ),
            dict(
                allocation_id="a2",
                claim_id="c2",
                collateral_id="k1",
                kind="HYP",
                currency="EUR",
                amount=40,
            ),
        ]
        originals = deepcopy((claims, collateral, allocations))
        r = p.validate_allocations(claims, collateral, allocations)
        self.assertEqual(r.details["collateral"]["k1"]["remaining"], 0)
        self.assertEqual(r.details["claims"]["c2"]["remaining"], 10)
        self.assertEqual((claims, collateral, allocations), originals)
        allocations[1]["amount"] = 50
        with self.assertRaises(p.PfandbriefError) as e:
            p.validate_allocations(claims, collateral, allocations)
        self.assertEqual(e.exception.code, "OVERALLOCATION")

    def test_events(self):
        a = dict(
            event_id="a",
            asset_id="x",
            kind="HYP",
            effective_date="2025-01-01",
            recorded_at="2025-01-01",
            sequence=1,
            action="ADD",
            payload={"amount": 100},
            reason="initial",
            evidence_ref="e1",
        )
        b = dict(
            a,
            event_id="b",
            effective_date="2025-02-01",
            recorded_at="2025-03-01",
            action="UPDATE",
            payload={"amount": 90},
        )
        self.assertEqual(
            p.register_snapshot([a, b], "2025-02-15", "2025-02-15").value[0]["payload"][
                "amount"
            ],
            100,
        )
        self.assertEqual(
            p.register_snapshot([a, b], "2025-02-15", "2025-03-02").value[0]["payload"][
                "amount"
            ],
            90,
        )
        self.assertEqual(a["payload"]["amount"], 100)
        with self.assertRaises(p.PfandbriefError) as e:
            p.register_snapshot([b], "2025-02-15", "2025-03-02")
        self.assertEqual(e.exception.code, "UNKNOWN_ASSET")
        self.assertEqual(p.register_snapshot([], "2025-02-15", "2025-03-02").value, [])


if __name__ == "__main__":
    unittest.main()
