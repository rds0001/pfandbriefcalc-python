"""Separate coverage, limits, stress and liquidity ledgers.

Copyright 2026 RiskDataScience GmbH. SPDX-License-Identifier: AGPL-3.0-only
"""

from datetime import timedelta
from .core import CalcResult, PfandbriefError, choice, number, flag, iso_date
from .controls import _records, _unique, _text
from .coverage import liquidity_gap
from .stress import stressed_fx_net

KINDS = ("HYP", "OEF", "SCH", "FLG")


def _kind(rows, kind):
    choice(kind, "kind", KINDS)
    for row in rows:
        if row["kind"] != kind:
            raise PfandbriefError(
                "KIND_MISMATCH", "each calculation contains exactly one Pfandbrief kind"
            )


def _limit(name, used, base, ratio, source):
    maximum = base * ratio
    return {
        "check": name,
        "used": used,
        "base": base,
        "ratio": ratio,
        "maximum": maximum,
        "headroom": maximum - used,
        "passed": used <= maximum,
        "source_ref": source,
    }


def pool_coverage(
    kind, assets, liabilities, oc_allocations, *, additional_nominal=0, additional_pv=0
):
    """Coverage of qualified single-currency amounts with disjoint OC reservations."""
    assets = _records(
        assets,
        ("asset_id", "kind", "nominal", "present_value", "pv_oc_eligible"),
        "assets",
    )
    debts = _records(
        liabilities,
        ("liability_id", "kind", "type", "nominal", "max_redemption", "present_value"),
        "liabilities",
    )
    alloc = _records(oc_allocations, ("asset_id", "role", "fraction"), "oc_allocations")
    _unique(assets, ("asset_id",))
    _unique(debts, ("liability_id",))
    _unique(alloc, ("asset_id", "role"))
    _kind(assets + debts, kind)
    extra_n = number(additional_nominal, "additional_nominal", 0)
    extra_p = number(additional_pv, "additional_pv", 0)
    asset_map = {}
    for row in assets:
        asset_map[row["asset_id"]] = {
            "nominal": number(row["nominal"], "nominal", 0),
            "present_value": number(row["present_value"], "present_value", 0),
            "pv_oc_eligible": flag(row["pv_oc_eligible"], "pv_oc_eligible"),
            "NOMINAL_OC": 0.0,
            "PV_OC": 0.0,
        }
    debt_n, debt_p, bond_n, bond_p, deriv_p = 0.0, 0.0, 0.0, 0.0, 0.0
    for row in debts:
        choice(row["type"], "type", ("BOND", "DERIVATIVE"))
        nominal = number(row["nominal"], "nominal", 0)
        redemption = number(row["max_redemption"], "max_redemption", 0)
        pv = number(row["present_value"], "present_value", 0)
        debt_n += max(nominal, redemption)
        debt_p += pv
        if row["type"] == "BOND":
            bond_n += nominal
            bond_p += pv
        else:
            deriv_p += pv
    for row in alloc:
        if row["asset_id"] not in asset_map:
            raise PfandbriefError("UNKNOWN_KEY", "OC references unknown asset")
        role = choice(row["role"], "role", ("NOMINAL_OC", "PV_OC"))
        fraction = number(row["fraction"], "fraction", 0, 1)
        item = asset_map[row["asset_id"]]
        if role == "PV_OC" and fraction > 0 and not item["pv_oc_eligible"]:
            raise PfandbriefError(
                "INELIGIBLE_OC", "PV OC requires a separately qualified asset"
            )
        item[role] = fraction
        if item["NOMINAL_OC"] + item["PV_OC"] > 1:
            raise PfandbriefError(
                "OVERALLOCATION", "same asset fraction reserved more than once"
            )
    total_n = sum(a["nominal"] for a in asset_map.values())
    total_p = sum(a["present_value"] for a in asset_map.values())
    nom_oc = sum(a["nominal"] * a["NOMINAL_OC"] for a in asset_map.values())
    pv_oc = sum(a["present_value"] * a["PV_OC"] for a in asset_map.values())
    pv_oc_n = sum(a["nominal"] * a["PV_OC"] for a in asset_map.values())
    q_n = 0.02 if kind in ("HYP", "OEF") else 0.05
    required_n, required_p = debt_n * q_n + extra_n, debt_p * 0.02 + extra_p
    checks = {
        "nominal_total": total_n - pv_oc_n >= debt_n + required_n,
        "nominal_reserved": nom_oc >= required_n,
        "nominal_base_unreserved": total_n - pv_oc_n - nom_oc >= debt_n,
        "present_value_total": total_p >= debt_p + required_p,
        "present_value_reserved": pv_oc >= required_p,
    }
    return CalcResult(
        "CHECKS_PASSED" if all(checks.values()) else "FAILED",
        "pool_coverage",
        ("PfandBG §4(1)–(3a)",),
        "decision",
        details={
            "kind": kind,
            "assets_nominal": total_n,
            "assets_pv": total_p,
            "liabilities_nominal": debt_n,
            "liabilities_pv": debt_p,
            "bond_nominal": bond_n,
            "bond_pv": bond_p,
            "derivative_liabilities_pv": deriv_p,
            "nominal_oc_rate": q_n,
            "required_nominal_oc": required_n,
            "required_pv_oc": required_p,
            "allocated_nominal_oc": nom_oc,
            "allocated_pv_oc": pv_oc,
            "pv_oc_nominal": pv_oc_n,
            "nominal_headroom": total_n - pv_oc_n - debt_n - required_n,
            "pv_headroom": total_p - debt_p - required_p,
            "checks": checks,
            "allocations": asset_map,
        },
        limitations=(
            "Amounts must be qualified, registered and expressed in one reporting currency",
            "Checks the supplied reservations; does not optimize or authenticate qualification",
        ),
    )


def pool_limits(kind, assets, bond_nominal, bond_pv, derivative_liabilities):
    """Statutory concentration arithmetic on explicitly classified qualified amounts."""
    fields = (
        "asset_id",
        "kind",
        "amount",
        "tier",
        "pv_oc_exempt_amount",
        "liquidity_only",
        "bank_group",
        "primary",
        "construction",
        "land",
        "foreign_bucket",
        "downgraded",
    )
    rows = _records(assets, fields, "assets")
    _unique(rows, ("asset_id",))
    _kind(rows, kind)
    derivs = _records(
        derivative_liabilities,
        ("liability_id", "kind", "present_value", "pure_fx_hedge"),
        "derivative_liabilities",
    )
    _unique(derivs, ("liability_id",))
    _kind(derivs, kind)
    bonds = number(bond_nominal, "bond_nominal", 0)
    bpv = number(bond_pv, "bond_pv", 0)
    tiers = {k: 0.0 for k in ("T1", "T2", "T3", "T4")}
    groups = {}
    total = primary = construction = land = downgraded = 0.0
    foreign = {
        k: 0.0
        for k in (
            "PRIMARY_PROTECTED",
            "PRIMARY_UNPROTECTED",
            "OTHER_PROTECTED",
            "OTHER_UNPROTECTED",
        )
    }
    for row in rows:
        amount = number(row["amount"], "amount", 0)
        tier = choice(
            row["tier"], "tier", ("PRIMARY", "T1", "T2", "T3", "T4", "UNLIMITED")
        )
        exempt = number(row["pv_oc_exempt_amount"], "pv_oc_exempt_amount", 0, amount)
        liquid = flag(row["liquidity_only"], "liquidity_only")
        pri = flag(row["primary"], "primary")
        con = flag(row["construction"], "construction")
        bare = flag(row["land"], "land")
        down = flag(row["downgraded"], "downgraded")
        bucket = choice(row["foreign_bucket"], "foreign_bucket", ("NONE", *foreign))
        if kind == "OEF" and tier == "T4":
            raise PfandbriefError(
                "INVALID_CLASSIFICATION", "OEF has no T4 substitution tier"
            )
        if exempt and tier not in ("T2", "T3", "T4"):
            raise PfandbriefError(
                "INVALID_EXEMPTION", "PV OC exemption is not applicable to this tier"
            )
        if (con or bare) and not pri:
            raise PfandbriefError(
                "INVALID_CLASSIFICATION",
                "construction/land requires primary collateral",
            )
        if bare and kind != "HYP":
            raise PfandbriefError("INVALID_CLASSIFICATION", "land flag applies to HYP")
        if (
            bucket.startswith("PRIMARY_")
            and not pri
            or bucket.startswith("OTHER_")
            and pri
        ):
            raise PfandbriefError(
                "INVALID_CLASSIFICATION", "foreign bucket must match primary flag"
            )
        if tier == "PRIMARY" and not pri or pri and tier != "PRIMARY":
            raise PfandbriefError(
                "INVALID_CLASSIFICATION", "primary flag and tier disagree"
            )
        total += amount
        if pri:
            primary += amount
            if con or bare:
                construction += amount
            if bare:
                land += amount
        if not liquid:
            if tier in tiers:
                tiers[tier] += amount - exempt
            if down:
                downgraded += amount
            if bucket != "NONE":
                foreign[bucket] += amount
        # Pure liquidity exemption covers §19/20/26/26f, not §13/22/26b.
        elif bucket.startswith("PRIMARY_") and kind != "OEF":
            foreign[bucket] += amount
        group = row["bank_group"]
        if group is not None:
            _text(group, "bank_group")
            if tier not in ("T1", "T2", "T3"):
                raise PfandbriefError(
                    "INVALID_CLASSIFICATION", "bank-group exposure must be in T1–T3"
                )
            if not liquid:
                groups[group] = groups.get(group, 0.0) + amount
    checks = []
    cumulative = 0.0
    for tier, ratio in (("T1", 0.08), ("T2", 0.10), ("T3", 0.15), ("T4", 0.20)):
        if kind == "OEF" and tier == "T4":
            continue
        cumulative += tiers[tier]
        checks.append(
            _limit(
                "substitution_" + tier,
                cumulative,
                bonds,
                ratio,
                "PfandBG §§19,20,26,26f",
            )
        )
    for group in sorted(groups):
        checks.append(
            _limit(
                "bank_group:" + group,
                groups[group],
                bonds,
                0.02,
                "PfandBG §19(1) sentence5; §§20,26,26f",
            )
        )
    if kind == "HYP":
        checks.extend(
            [
                _limit(
                    "construction_and_land", construction, total, 0.10, "PfandBG §16(3)"
                ),
                _limit("land", land, total, 0.01, "PfandBG §16(3)"),
            ]
        )
    if kind == "SCH":
        checks.append(
            _limit("ship_construction", construction, primary, 0.20, "PfandBG §24(4)")
        )
    if kind == "OEF":
        checks.append(
            _limit(
                "unprotected_public",
                foreign["PRIMARY_UNPROTECTED"] + foreign["OTHER_UNPROTECTED"],
                foreign["PRIMARY_PROTECTED"] + foreign["OTHER_PROTECTED"],
                0.10,
                "PfandBG §20(3)",
            )
        )
    else:
        checks.append(
            _limit(
                "unprotected_primary",
                foreign["PRIMARY_UNPROTECTED"],
                foreign["PRIMARY_PROTECTED"],
                0.10 if kind == "HYP" else 0.20,
                "PfandBG §§13,22(5),26b(4)",
            )
        )
        checks.append(
            _limit(
                "unprotected_other",
                foreign["OTHER_UNPROTECTED"],
                foreign["OTHER_PROTECTED"],
                0.10,
                "PfandBG §20(3); §§19,26,26f",
            )
        )
    checks.append(
        _limit("downgraded_public", downgraded, bonds, 0.20, "PfandBG §20(1)3; §49(2)")
    )
    dpv = 0.0
    for row in derivs:
        value = number(row["present_value"], "present_value", 0)
        if not flag(row["pure_fx_hedge"], "pure_fx_hedge"):
            dpv += value
    checks.append(
        _limit("derivative_liabilities", dpv, bpv + dpv, 0.12, "PfandBG §4b(3)")
    )
    return CalcResult(
        "CHECKS_PASSED" if all(c["passed"] for c in checks) else "FAILED",
        "pool_limits",
        ("PfandBG §§4b,13,16,19,20,22,24,26,26b,26f,49",),
        "decision",
        details={
            "kind": kind,
            "checks": checks,
            "tiers": tiers,
            "bank_groups": groups,
            "foreign": foreign,
            "total_assets": total,
            "primary_assets": primary,
        },
        limitations=(
            "Classification, exemptions, foreign priority and any special permissions require separate evidence",
            "No generic exemption from the bank-group limit for PV OC assets",
        ),
    )


def pool_stress(kind, valuations, fx_rates):
    """Net stressed values by currency, then apply adverse FX; three scenarios required."""
    fields = ("position_id", "kind", "currency", "scenario", "signed_present_value")
    rows = _records(valuations, fields, "valuations")
    _unique(rows, ("position_id", "scenario"))
    _kind(rows, kind)
    fx = _records(fx_rates, ("currency", "eur_per_unit", "shock"), "fx_rates")
    _unique(fx, ("currency",))
    rates = {}
    for row in fx:
        rate = number(row["eur_per_unit"], "eur_per_unit", 0, strict_min=True)
        shock = number(row["shock"], "shock", 0)
        if row["currency"] == "EUR" and (rate != 1 or shock != 0):
            raise PfandbriefError("INVALID_FX", "EUR requires rate1 and shock0")
        rates[row["currency"]] = (rate, shock)
    ids = {}
    scenarios = {s: {} for s in ("BASE", "UP", "DOWN")}
    for row in rows:
        scenario = choice(row["scenario"], "scenario", scenarios)
        cur = _text(row["currency"], "currency")
        ident = row["position_id"]
        if cur not in rates:
            raise PfandbriefError("MISSING_FX", "missing currency conversion/stress")
        if ident in ids and ids[ident] != cur:
            raise PfandbriefError(
                "CURRENCY_MISMATCH", "position currency changed across scenarios"
            )
        ids[ident] = cur
        value = number(row["signed_present_value"], "signed_present_value")
        scenarios[scenario][ident] = value
    if not ids or any(set(s) != set(ids) for s in scenarios.values()):
        raise PfandbriefError(
            "MISSING_SCENARIO", "every position needs BASE, UP and DOWN"
        )
    results = {}
    for scenario, values in scenarios.items():
        net = {cur: 0.0 for cur in sorted(set(ids.values()))}
        for ident, value in values.items():
            net[ids[ident]] += value
        stressed = {
            cur: (
                value * rates[cur][0]
                if scenario == "BASE"
                else stressed_fx_net(value, *rates[cur]).value
            )
            for cur, value in net.items()
        }
        results[scenario] = {
            "currency_net": net,
            "eur_net": stressed,
            "balance": sum(stressed.values()),
        }
    worst = min(v["balance"] for v in results.values())
    return CalcResult(
        max(0.0, -worst),
        "pool_stress",
        ("PfandBarwertV §§4–6; PfandBG §4(1) sentence1",),
        "EUR",
        details={
            "kind": kind,
            "scenarios": results,
            "worst_balance": worst,
            "arithmetic_pass": worst >= 0,
        },
        limitations=(
            "Each scenario must contain independently qualified valuations and all derivative liabilities",
            "Separate base PV OC requirement is checked by pool_coverage",
        ),
    )


def liquidity_180(as_of, cashflows, buffers):
    """Exactly 180 following calendar days; no assumed maturity extension or reinvestment."""
    day = iso_date(as_of, "as_of")
    flows = _records(
        cashflows, ("flow_id", "position_id", "date", "inflow", "outflow"), "cashflows"
    )
    _unique(flows, ("flow_id",))
    assets = _records(
        buffers,
        ("asset_id", "qualified_value", "monetized", "qualification_ref"),
        "buffers",
    )
    _unique(assets, ("asset_id",))
    amount = 0.0
    monetized = set()
    for row in assets:
        amount += number(row["qualified_value"], "qualified_value", 0)
        if flag(row["monetized"], "monetized"):
            monetized.add(row["asset_id"])
        _text(row["qualification_ref"], "qualification_ref")
    ins, outs, excluded = [0.0] * 180, [0.0] * 180, []
    for row in flows:
        _text(row["position_id"], "position_id")
        delta = (iso_date(row["date"], "date") - day).days
        incoming = number(row["inflow"], "inflow", 0)
        outgoing = number(row["outflow"], "outflow", 0)
        if delta <= 0:
            raise PfandbriefError(
                "PAST_CASHFLOW", "supply future contractual flows only"
            )
        if delta > 180:
            continue
        if row["position_id"] in monetized and incoming:
            excluded.append(row["flow_id"])
            incoming = 0.0
        ins[delta - 1] += incoming
        outs[delta - 1] += outgoing
    result = liquidity_gap(ins, outs, amount)
    return CalcResult(
        result.value,
        "liquidity_180",
        ("PfandBG §4(1a); LCR Art9–12",),
        "currency",
        details={
            **result.details,
            "as_of": day.isoformat(),
            "dates": [(day + timedelta(days=i)).isoformat() for i in range(1, 181)],
            "inflows": ins,
            "outflows": outs,
            "excluded_monetized_inflows": excluded,
        },
        limitations=(
            "Buffer qualification and amounts must be supplied separately in the cashflow reporting currency",
            "Monetized assets lose their contractual inflows; payments owed remain included",
        ),
    )
