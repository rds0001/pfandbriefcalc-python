"""Synthetic, deterministic worked pools; never customer data or real attestations.

Copyright 2026 RiskDataScience GmbH. SPDX-License-Identifier: AGPL-3.0-only
"""

from .core import CalcResult, choice, number
from .portfolio import pool_requirements
from .finance import coupon_schedule, contract_cashflows, year_fraction
from .advanced import cashflow_scenarios
from .eu import liquid_buffer_value


def _fictional_evidence(requirements):
    return [
        dict(
            evidence_id="SYNTHETIC:" + r["scope"] + ":" + r["requirement_id"],
            requirement_id=r["requirement_id"],
            scope=r["scope"],
            valid_from="2026-11-11",
            valid_to="2026-11-11",
            known_from="2026-11-11",
            conclusion="MET",
            reviewer="SYNTHETIC EXAMPLE; NO REAL REVIEWER",
            source_ref=r["source_ref"],
            reason="Fictional assumption solely for the worked software example",
        )
        for r in requirements
    ]


def example_pool(kind, *, scale=1000000):
    """Build a synthetic EUR par-value pool and explicitly fictional evidence."""
    choice(kind, "kind", ("HYP", "OEF", "SCH", "FLG"))
    scale = number(scale, "scale", 0, strict_min=True)
    category = {"HYP": "MORTGAGE", "OEF": "PUBLIC", "SCH": "SHIP", "FLG": "AIRCRAFT"}[
        kind
    ]
    reserve = 2 if kind in ("HYP", "OEF") else 5
    positions = []
    for ident, quantity in (("primary", 100), ("nominal_oc", reserve), ("pv_oc", 2)):
        is_pv = ident == "pv_oc"
        cat = "SUBSTITUTE" if is_pv and kind != "OEF" else category
        amount = quantity * scale
        amounts = dict(
            claim=amount,
            registered=amount,
            redemption=amount,
            defaulted=False,
            guaranteed=False,
            guarantor_defaulted=False,
        )
        if cat in ("MORTGAGE", "SHIP", "AIRCRAFT"):
            amounts.update(lien=amount, lending_value=2 * amount, prior_claims=0.0)
        positions.append(
            dict(
                position_id=ident,
                kind=kind,
                category=cat,
                currency="EUR",
                amounts=amounts,
                pv_base=amount,
                pv_up=amount,
                pv_down=amount,
                features=[],
                limits=dict(
                    tier="T4" if cat == "SUBSTITUTE" else "PRIMARY",
                    bank_group=None,
                    construction=False,
                    land=False,
                    foreign_bucket="OTHER_PROTECTED"
                    if cat == "SUBSTITUTE"
                    else "PRIMARY_PROTECTED",
                    downgraded=False,
                    liquidity_only=False,
                    pv_oc_exempt=cat == "SUBSTITUTE",
                ),
            )
        )
    positions.append(
        dict(
            position_id="bond",
            kind=kind,
            category="BOND",
            currency="EUR",
            amounts=dict(
                nominal=100 * scale, max_redemption=100 * scale, own_held_excluded=False
            ),
            pv_base=100 * scale,
            pv_up=100 * scale,
            pv_down=100 * scale,
            features=[],
            limits={},
        )
    )
    allocations = [
        dict(asset_id="nominal_oc", role="NOMINAL_OC", fraction=1.0),
        dict(asset_id="pv_oc", role="PV_OC", fraction=1.0),
    ]
    args = dict(
        kind=kind,
        positions=positions,
        oc_allocations=allocations,
        cashflows=[],
        buffers=[],
        fx_rates=[dict(currency="EUR", eur_per_unit=1.0, shock=0.0)],
        evidence=[],
        as_of="2026-11-11",
        known_at="2026-11-11",
    )
    requirements = pool_requirements(kind, positions, allocations, []).value
    args["evidence"] = _fictional_evidence(requirements)
    return CalcResult(
        args,
        "example_pool",
        unit="input_bundle",
        details={
            "synthetic": True,
            "scale": scale,
            "basis": "Stylized par-valued positions; externally supplied equal scenario prices",
        },
        limitations=(
            "All evidence and scenario values are fictional; never reuse as actual regulatory evidence",
            "No cashflows within 180 days assumed; this example illustrates integration, not realistic interest-rate dynamics",
        ),
    )


def cashflow_example_pool(kind, *, scale=1000000):
    """Synthetic cashflow-to-pool example with genuine repricing and a coupon liquidity gap."""
    args = example_pool(kind, scale=scale).value
    scale = number(scale, "scale", 0, strict_min=True)
    schedules, cashflow_values = {}, {}
    for p in args["positions"]:
        ident = p["position_id"]
        bond = p["category"] == "BOND"
        if ident in ("primary", "pv_oc"):
            amount = (120 if ident == "primary" else 5) * scale
            for key in ("claim", "registered", "redemption"):
                p["amounts"][key] = amount
            if "lien" in p["amounts"]:
                p["amounts"].update(lien=amount, lending_value=2 * amount)
        amount = p["amounts"]["nominal" if bond else "claim"]
        schedule = coupon_schedule(
            "2026-11-11",
            "2028-11-11",
            4 if bond else 1,
            "30E/360",
            "modified_following",
            [],
        ).value
        flows = contract_cashflows(
            schedule, amount, [0.04] * len(schedule), [0.0] * len(schedule)
        ).value
        times = [
            year_fraction(args["as_of"], f["payment_date"], "ACT/365F").value
            for f in flows
        ]
        values = cashflow_scenarios(
            [f["amount"] for f in flows],
            times,
            [0.0, 3.0],
            [0.03, 0.03],
            method="static",
        )
        for scenario, value in values.value.items():
            p["pv_" + scenario.lower()] = value
        for i, f in enumerate(flows):
            args["cashflows"].append(
                dict(
                    flow_id=ident + ":" + str(i + 1),
                    position_id=ident,
                    date=f["payment_date"],
                    inflow=0.0 if bond else f["amount"],
                    outflow=f["amount"] if bond else 0.0,
                )
            )
        schedules[ident] = schedule
        cashflow_values[ident] = values.as_dict()
    buffer_value = liquid_buffer_value(
        next(p for p in args["positions"] if p["position_id"] == "pv_oc")["pv_base"],
        "LEVEL1_OTHER",
        qualification_status="MET",
    ).value
    args["buffers"] = [
        dict(
            asset_id="pv_oc",
            qualified_value=buffer_value,
            monetized=True,
            qualification_ref="SYNTHETIC: qualifying sovereign security; independently assumed fair market value",
        )
    ]
    args["evidence"] = _fictional_evidence(
        pool_requirements(
            kind, args["positions"], args["oc_allocations"], args["buffers"]
        ).value
    )
    return CalcResult(
        args,
        "cashflow_example_pool",
        unit="input_bundle",
        details={
            "synthetic": True,
            "scale": scale,
            "schedules": schedules,
            "valuations": cashflow_values,
            "curve_times": [0.0, 3.0],
            "zero_rates": [0.03, 0.03],
            "coupon_rate": 0.04,
            "independent_liquidity_oracle": scale,
        },
        limitations=(
            "All legal evidence is fictional; supplied scenario prices are now computed from disclosed cashflows",
            "Illustrative annual asset coupons and quarterly bond coupons; no customer data or actual market quotation",
        ),
    )
