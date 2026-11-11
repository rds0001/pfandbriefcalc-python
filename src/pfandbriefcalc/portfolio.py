"""One position universe for native, auditable Pfandbrief pool calculations.

Copyright 2026 RiskDataScience GmbH. SPDX-License-Identifier: AGPL-3.0-only
"""

from copy import deepcopy
from .core import CalcResult, PfandbriefError, number, flag, choice, iso_date
from .controls import _records, _unique, _text, assess_evidence
from .eligibility import cover_amount, required_evidence
from .pools import _kind, pool_coverage, pool_limits, pool_stress, liquidity_180


def _positions(positions, kind):
    fields = (
        "position_id",
        "kind",
        "category",
        "currency",
        "amounts",
        "pv_base",
        "pv_up",
        "pv_down",
        "features",
        "limits",
    )
    rows = _records(positions, fields, "positions")
    _unique(rows, ("position_id",))
    _kind(rows, kind)
    if not rows:
        raise PfandbriefError("EMPTY_POOL", "provide a nonempty position universe")
    for r in rows:
        _text(r["currency"], "currency")
        if not isinstance(r["amounts"], dict) or not isinstance(r["limits"], dict):
            raise PfandbriefError(
                "INVALID_TABLE", "amounts and limits must be mappings"
            )
        required_evidence(kind, r["position_id"], r["category"], r["features"])
    return rows


def pool_requirements(kind, positions, oc_allocations, buffers):
    """Derive all mandatory position and pool evidence before an integrated run."""
    rows = _positions(positions, kind)
    alloc = _records(oc_allocations, ("asset_id", "role", "fraction"), "oc_allocations")
    buf = _records(
        buffers,
        ("asset_id", "qualified_value", "monetized", "qualification_ref"),
        "buffers",
    )
    _unique(alloc, ("asset_id", "role"))
    _unique(buf, ("asset_id",))
    ids = {r["position_id"] for r in rows}
    for r in alloc + buf:
        if r["asset_id"] not in ids:
            raise PfandbriefError(
                "UNKNOWN_KEY", "OC/buffer references unknown position"
            )
    pv = set()
    for r in alloc:
        role = choice(r["role"], "role", ("PV_OC", "NOMINAL_OC"))
        if number(r["fraction"], "fraction", 0, 1) > 0 and role == "PV_OC":
            pv.add(r["asset_id"])
    liquid = {
        r["asset_id"]
        for r in buf
        if number(r["qualified_value"], "qualified_value", 0) > 0
    }
    result = []
    for r in rows:
        features = list(r["features"])
        amount = r["amounts"]
        automatic = []
        if r["position_id"] in pv:
            automatic.append("pv_oc")
        if r["position_id"] in liquid or r["limits"].get("liquidity_only", False):
            automatic.append("liquidity")
        if r["category"] == "BOND":
            if amount.get("own_held_excluded", False):
                automatic.append("own_held")
        elif r["category"] != "DERIVATIVE":
            if amount.get("guaranteed", False):
                automatic.append("guaranteed")
            if (
                "registered" in amount
                and "claim" in amount
                and number(amount["registered"], "registered", 0)
                < number(amount["claim"], "claim", 0)
            ):
                automatic.append("partial")
            if amount.get("lending_limit", 0.60) != 0.60:
                automatic.append("exception")
        features.extend(f for f in automatic if f not in features)
        result.extend(
            required_evidence(kind, r["position_id"], r["category"], features).value
        )
    pool = {
        "profile_applicability": "Selected local rule edition; PfandBG §§45–55",
        "complete_position_universe": "PfandBG §§4(4),5; complete register/issue reconciliation",
        "valuation_method": "PfandBarwertV §§2–7; curves, options, independent prices and method continuity",
        "operational_governance": "PfandBG §§2,7–11,27,29–36a",
        "additional_requirements": "PfandBG §4(3a)–(3b); explicit additional amount inputs",
    }
    result.extend(
        {
            "requirement_id": k,
            "scope": "POOL:" + kind,
            "allow_not_applicable": False,
            "source_ref": v,
        }
        for k, v in pool.items()
    )
    return CalcResult(result, "pool_requirements", tuple(pool.values()), "records")


def analyze_pool(
    kind,
    positions,
    oc_allocations,
    cashflows,
    buffers,
    fx_rates,
    evidence,
    as_of,
    known_at,
    *,
    additional_nominal=0,
    additional_pv=0,
):
    """Integrate explicit valuations, coverage, limits, liquidity and dated evidence in EUR."""
    rows = _positions(positions, kind)
    day = iso_date(as_of, "as_of")
    knowledge = iso_date(known_at, "known_at")
    requirements = pool_requirements(kind, rows, oc_allocations, buffers).value
    proof = assess_evidence(requirements, evidence, day, knowledge)
    proof_rows = proof.details["checks"]
    failed = {
        r["scope"]
        for r in proof_rows
        if r["status"] in ("NOT_MET", "INVALID_NOT_APPLICABLE")
    }
    own_proven = {
        r["scope"]
        for r in proof_rows
        if r["requirement_id"] == "feature_own_held" and r["status"] == "MET"
    }
    fx = _records(fx_rates, ("currency", "eur_per_unit", "shock"), "fx_rates")
    _unique(fx, ("currency",))
    rates = {
        r["currency"]: number(r["eur_per_unit"], "eur_per_unit", 0, strict_min=True)
        for r in fx
    }
    pmap = {r["position_id"]: r for r in rows}
    allocations = _records(
        oc_allocations, ("asset_id", "role", "fraction"), "oc_allocations"
    )
    pv_fractions = {
        r["asset_id"]: r["fraction"] for r in allocations if r["role"] == "PV_OC"
    }
    assets, debts, limits, derivatives, stresses, atomic = [], [], [], [], [], []
    excluded = set()
    positive_disabled = set()
    nominal_by_id = {}
    for r in rows:
        ident, category, currency = r["position_id"], r["category"], r["currency"]
        if currency not in rates:
            raise PfandbriefError(
                "MISSING_FX", "all positions require an explicit FX rate"
            )
        rate = rates[currency]
        values = {
            s: number(
                r["pv_" + s.lower()],
                "pv_" + s.lower(),
                None if category == "DERIVATIVE" else 0,
            )
            for s in ("BASE", "UP", "DOWN")
        }
        eligibility_failed = ident in failed
        if category == "BOND":
            a = _records(
                [r["amounts"]],
                ("nominal", "max_redemption", "own_held_excluded"),
                "bond amounts",
            )[0]
            n, redemption = (
                number(a["nominal"], "nominal", 0),
                number(a["max_redemption"], "max_redemption", 0),
            )
            own = flag(a["own_held_excluded"], "own_held_excluded")
            remove = own and ident in own_proven and not eligibility_failed
            if remove:
                excluded.add(ident)
            factor = 0.0 if remove else 1.0
            debts.append(
                {
                    "liability_id": ident,
                    "kind": kind,
                    "type": "BOND",
                    "nominal": n * rate * factor,
                    "max_redemption": redemption * rate * factor,
                    "present_value": values["BASE"] * rate * factor,
                }
            )
            nominal_by_id[ident] = max(n, redemption) * rate * factor
            values = {s: -v * factor for s, v in values.items()}
        else:
            if category == "DERIVATIVE":
                if r["amounts"]:
                    raise PfandbriefError(
                        "NOT_APPLICABLE",
                        "derivative closeout amount comes from independent base market value",
                    )
                nominal = max(0.0, values["BASE"])
                pure = flag(r["limits"].get("pure_fx_hedge"), "pure_fx_hedge")
                debt = max(0.0, -values["BASE"]) * rate
                debts.append(
                    {
                        "liability_id": ident,
                        "kind": kind,
                        "type": "DERIVATIVE",
                        "nominal": debt,
                        "max_redemption": debt,
                        "present_value": debt,
                    }
                )
                derivatives.append(
                    {
                        "liability_id": ident,
                        "kind": kind,
                        "present_value": debt,
                        "pure_fx_hedge": pure,
                    }
                )
            else:
                allowed = {
                    "claim",
                    "registered",
                    "redemption",
                    "defaulted",
                    "guaranteed",
                    "guarantor_defaulted",
                    "lien",
                    "lending_value",
                    "prior_claims",
                    "guarantee_amount",
                    "lending_limit",
                }
                required = (
                    "claim",
                    "registered",
                    "redemption",
                    "defaulted",
                    "guaranteed",
                    "guarantor_defaulted",
                )
                args = _records([r["amounts"]], required, "asset amounts")[0]
                if set(args) - allowed:
                    raise PfandbriefError(
                        "UNKNOWN_FIELD", "unknown cover amount parameter"
                    )
                amount = cover_amount(category, **args)
                nominal = amount.value
                if amount.details["default_excluded"]:
                    eligibility_failed = True
                if (
                    nominal == 0
                    and any(v > 0 for v in values.values())
                    and not eligibility_failed
                ):
                    raise PfandbriefError(
                        "INCONSISTENT_VALUE",
                        "positive asset PV with zero qualified nominal tranche",
                    )
            if eligibility_failed:
                positive_disabled.add(ident)
                nominal = 0.0
                values = {s: min(0.0, v) for s, v in values.items()}
            nominal_by_id[ident] = nominal * rate
            assets.append(
                {
                    "asset_id": ident,
                    "kind": kind,
                    "nominal": nominal * rate,
                    "present_value": max(0.0, values["BASE"]) * rate,
                    "pv_oc_eligible": ident in pv_fractions,
                }
            )
            lim_fields = (
                "tier",
                "bank_group",
                "construction",
                "land",
                "foreign_bucket",
                "downgraded",
                "liquidity_only",
                "pv_oc_exempt",
            )
            lim = _records([r["limits"]], lim_fields, "limits")[0]
            exempt = flag(lim["pv_oc_exempt"], "pv_oc_exempt")
            if category == "DERIVATIVE" and (ident in pv_fractions or exempt):
                raise PfandbriefError(
                    "INELIGIBLE_OC", "derivatives are not qualifying PV OC instruments"
                )
            limits.append(
                {
                    "asset_id": ident,
                    "kind": kind,
                    "amount": nominal * rate,
                    **{
                        k: lim[k]
                        for k in (
                            "tier",
                            "bank_group",
                            "construction",
                            "land",
                            "foreign_bucket",
                            "downgraded",
                            "liquidity_only",
                        )
                    },
                    "primary": category in ("MORTGAGE", "PUBLIC", "SHIP", "AIRCRAFT"),
                    "pv_oc_exempt_amount": nominal * rate * pv_fractions.get(ident, 0.0)
                    if exempt
                    else 0.0,
                }
            )
        for scenario, value in values.items():
            stresses.append(
                {
                    "position_id": ident,
                    "kind": kind,
                    "currency": currency,
                    "scenario": scenario,
                    "signed_present_value": value,
                }
            )
        atomic.append(
            {
                "position_id": ident,
                "category": category,
                "currency": currency,
                "nominal_eur": nominal_by_id[ident],
                "signed_base_pv_eur": values["BASE"] * rate,
                "positive_excluded": ident in positive_disabled,
                "own_held_excluded": ident in excluded,
            }
        )
    coverage = pool_coverage(
        kind,
        assets,
        debts,
        allocations,
        additional_nominal=additional_nominal,
        additional_pv=additional_pv,
    )
    concentration = pool_limits(
        kind,
        limits,
        coverage.details["bond_nominal"],
        coverage.details["bond_pv"],
        derivatives,
    )
    stress = pool_stress(kind, stresses, fx)
    flow_rows = _records(
        cashflows, ("flow_id", "position_id", "date", "inflow", "outflow"), "cashflows"
    )
    _unique(flow_rows, ("flow_id",))
    translated_flows = []
    for r in flow_rows:
        ident = _text(r["position_id"], "position_id")
        if ident not in pmap:
            raise PfandbriefError("UNKNOWN_KEY", "cashflow references unknown position")
        inc, out = number(r["inflow"], "inflow", 0), number(r["outflow"], "outflow", 0)
        if ident in excluded:
            inc = out = 0.0
        if ident in positive_disabled:
            inc = 0.0
        rate = rates[pmap[ident]["currency"]]
        translated_flows.append({**r, "inflow": inc * rate, "outflow": out * rate})
    buffer_rows = _records(
        buffers,
        ("asset_id", "qualified_value", "monetized", "qualification_ref"),
        "buffers",
    )
    translated_buffers = []
    for r in buffer_rows:
        ident = r["asset_id"]
        p = pmap[ident]
        if p["category"] in ("BOND", "DERIVATIVE"):
            raise PfandbriefError(
                "INVALID_BUFFER",
                "bond liabilities and derivatives cannot be liquidity buffers",
            )
        value = number(r["qualified_value"], "qualified_value", 0)
        if nominal_by_id[ident] == 0:
            value = 0.0
        translated_buffers.append(
            {**r, "qualified_value": value * rates[p["currency"]]}
        )
    liquidity = liquidity_180(day, translated_flows, translated_buffers)
    arithmetic = (
        coverage.value == concentration.value == "CHECKS_PASSED"
        and stress.details["arithmetic_pass"]
        and liquidity.details["arithmetic_pass"]
    )
    decision = "FAILED" if not arithmetic or proof.value == "FAILED" else proof.value
    return CalcResult(
        decision,
        "analyze_pool",
        ("PfandBG §§4–26f; PfandBarwertV; explicit local rule applicability evidence",),
        "decision",
        details={
            "kind": kind,
            "as_of": day.isoformat(),
            "known_at": knowledge.isoformat(),
            "currency": "EUR",
            "coverage": coverage.as_dict(),
            "limits": concentration.as_dict(),
            "stress": stress.as_dict(),
            "liquidity": liquidity.as_dict(),
            "evidence": proof.as_dict(),
            "positions": atomic,
            "hypothetical": proof.value != "CHECKS_PASSED",
            "arithmetic_pass": arithmetic,
            "requirements": deepcopy(requirements),
        },
        limitations=(
            "CHECKS_PASSED covers implemented calculations and supplied evidence consistency, not authenticity or supervisory approval",
            "PV inputs must already value the qualified tranche; derivatives are independent framework market values",
            "Open evidence makes the otherwise calculated amounts hypothetical",
        ),
    )
