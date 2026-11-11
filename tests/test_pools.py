import unittest
from datetime import date, timedelta
from pfandbriefcalc import (
    pool_coverage,
    pool_limits,
    pool_stress,
    liquidity_180,
    PfandbriefError,
)


def asset(ident, amount, kind="HYP", **kwargs):
    return dict(
        asset_id=ident,
        kind=kind,
        nominal=amount,
        present_value=amount,
        pv_oc_eligible=True,
        **kwargs,
    )


def limit_asset(ident, amount, kind="HYP", **kwargs):
    r = dict(
        asset_id=ident,
        kind=kind,
        amount=amount,
        tier="PRIMARY",
        pv_oc_exempt_amount=0,
        liquidity_only=False,
        bank_group=None,
        primary=True,
        construction=False,
        land=False,
        foreign_bucket="PRIMARY_PROTECTED",
        downgraded=False,
    )
    r.update(kwargs)
    return r


class Pools(unittest.TestCase):
    def test_four_kinds_and_distinct_oc(self):
        for kind in ("HYP", "OEF", "SCH", "FLG"):
            reserve = 2 if kind in ("HYP", "OEF") else 5
            assets = [
                asset("base", 100, kind),
                asset("n", reserve, kind),
                asset("p", 2, kind),
            ]
            debts = [
                dict(
                    liability_id="bond",
                    kind=kind,
                    type="BOND",
                    nominal=100,
                    max_redemption=100,
                    present_value=100,
                )
            ]
            alloc = [
                dict(asset_id="n", role="NOMINAL_OC", fraction=1),
                dict(asset_id="p", role="PV_OC", fraction=1),
            ]
            result = pool_coverage(kind, assets, debts, alloc)
            self.assertEqual(result.value, "CHECKS_PASSED")
            self.assertEqual(result.details["nominal_headroom"], 0)
            assets[0]["nominal"] = 98
            self.assertEqual(pool_coverage(kind, assets, debts, alloc).value, "FAILED")
            alloc[0]["asset_id"] = "p"
            with self.assertRaisesRegex(PfandbriefError, "OVERALLOCATION"):
                pool_coverage(kind, assets, debts, alloc)

    def test_redemption_and_derivative_debt(self):
        assets = [asset("a", 110), asset("n", 3), asset("p", 3)]
        alloc = [
            dict(asset_id="n", role="NOMINAL_OC", fraction=1),
            dict(asset_id="p", role="PV_OC", fraction=1),
        ]
        debt = [
            dict(
                liability_id="b",
                kind="HYP",
                type="BOND",
                nominal=100,
                max_redemption=105,
                present_value=102,
            ),
            dict(
                liability_id="d",
                kind="HYP",
                type="DERIVATIVE",
                nominal=5,
                max_redemption=5,
                present_value=4,
            ),
        ]
        r = pool_coverage("HYP", assets, debt, alloc)
        self.assertEqual(r.details["liabilities_nominal"], 110)
        self.assertEqual(r.details["liabilities_pv"], 106)
        self.assertAlmostEqual(r.details["required_pv_oc"], 2.12)
        debt[0]["kind"] = "OEF"
        with self.assertRaisesRegex(PfandbriefError, "KIND_MISMATCH"):
            pool_coverage("HYP", assets, debt, alloc)

    def test_limits_boundaries_and_exemption(self):
        rows = [
            limit_asset("protected", 100),
            limit_asset("foreign", 10, foreign_bucket="PRIMARY_UNPROTECTED"),
            limit_asset(
                "bank",
                2,
                tier="T2",
                primary=False,
                bank_group="g",
                foreign_bucket="OTHER_PROTECTED",
                pv_oc_exempt_amount=2,
            ),
        ]
        r = pool_limits("HYP", rows, 100, 100, [])
        self.assertEqual(r.value, "CHECKS_PASSED")
        self.assertEqual(r.details["tiers"]["T2"], 0)
        rows[2]["amount"] = 2.01
        rows[2]["pv_oc_exempt_amount"] = 2.01
        self.assertEqual(pool_limits("HYP", rows, 100, 100, []).value, "FAILED")
        rows[2]["liquidity_only"] = True
        self.assertEqual(pool_limits("HYP", rows, 100, 100, []).value, "CHECKS_PASSED")
        rows[1]["amount"] = 10.01
        self.assertEqual(pool_limits("HYP", rows, 100, 100, []).value, "FAILED")
        # OEF denominator includes protected primary and other claims together.
        public = [
            limit_asset("p", 50, "OEF"),
            limit_asset(
                "q",
                50,
                "OEF",
                tier="UNLIMITED",
                primary=False,
                foreign_bucket="OTHER_PROTECTED",
            ),
            limit_asset("u", 10, "OEF", foreign_bucket="PRIMARY_UNPROTECTED"),
        ]
        self.assertEqual(
            pool_limits("OEF", public, 100, 100, []).value, "CHECKS_PASSED"
        )

    def test_construction_cumulative_and_derivatives(self):
        rows = [limit_asset("base", 90), limit_asset("site", 10, construction=True)]
        self.assertEqual(
            pool_limits(
                "HYP",
                rows,
                100,
                88,
                [
                    dict(
                        liability_id="d",
                        kind="HYP",
                        present_value=12,
                        pure_fx_hedge=False,
                    )
                ],
            ).value,
            "CHECKS_PASSED",
        )
        rows[1]["land"] = True
        self.assertEqual(pool_limits("HYP", rows, 100, 100, []).value, "FAILED")
        substitutes = [
            limit_asset(
                "t1", 8, tier="T1", primary=False, foreign_bucket="OTHER_PROTECTED"
            ),
            limit_asset(
                "t2", 2.01, tier="T2", primary=False, foreign_bucket="OTHER_PROTECTED"
            ),
        ]
        self.assertEqual(pool_limits("HYP", substitutes, 100, 100, []).value, "FAILED")

    def test_stress_currency_netting_and_completeness(self):
        rows = []
        for scenario, a in (("BASE", 104), ("UP", 98), ("DOWN", 105)):
            for ident, pv in (("asset", a), ("bond", -100)):
                rows.append(
                    dict(
                        position_id=ident,
                        kind="HYP",
                        currency="USD",
                        scenario=scenario,
                        signed_present_value=pv,
                    )
                )
        fx = [dict(currency="USD", eur_per_unit=0.5, shock=0.2)]
        r = pool_stress("HYP", rows, fx)
        self.assertEqual(r.value, 1.2)  # UP: net -2 USD -> -1 EUR minus .2 adverse FX.
        self.assertEqual(r.details["scenarios"]["DOWN"]["balance"], 2)
        with self.assertRaisesRegex(PfandbriefError, "MISSING_SCENARIO"):
            pool_stress("HYP", rows[:-1], fx)

    def test_180_days_and_monetization(self):
        day = date(2026, 1, 1)
        flows = [
            dict(
                flow_id="out",
                position_id="bond",
                date=str(day + timedelta(days=1)),
                inflow=0,
                outflow=50,
            ),
            dict(
                flow_id="in",
                position_id="asset",
                date=str(day + timedelta(days=180)),
                inflow=100,
                outflow=0,
            ),
            dict(
                flow_id="later",
                position_id="bond",
                date=str(day + timedelta(days=181)),
                inflow=0,
                outflow=999,
            ),
        ]
        buffers = [
            dict(
                asset_id="asset",
                qualified_value=50,
                monetized=True,
                qualification_ref="review",
            )
        ]
        r = liquidity_180(str(day), flows, buffers)
        self.assertEqual(r.value, 50)
        self.assertEqual(len(r.details["cumulative"]), 180)
        self.assertEqual(r.details["cumulative"][-1], -50)
        self.assertEqual(r.details["excluded_monetized_inflows"], ["in"])
        self.assertTrue(r.details["arithmetic_pass"])


if __name__ == "__main__":
    unittest.main()
