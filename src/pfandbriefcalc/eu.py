"""Covered-bond-specific EU arithmetic; no general credit-risk or LCR engine.

Copyright 2026 RiskDataScience GmbH. SPDX-License-Identifier: AGPL-3.0-only
"""

from .core import CalcResult, PfandbriefError, number, choice, flag, iso_date
from .controls import _records, _unique
from .pools import _limit, KINDS
from .finance import _month_date


def _proof(value, name):
    return choice(value, name, ("MET", "NOT_MET", "MISSING"))


def covered_bond_risk_weight(*, eligibility_status, cqs=None, issuer_risk_weight=None):
    """CRR Art129 mapping, conditional on separately established full eligibility."""
    proof = _proof(eligibility_status, "eligibility_status")
    if (cqs is None) == (issuer_risk_weight is None):
        raise PfandbriefError(
            "AMBIGUOUS_RATING",
            "supply either directly applicable CQS or unrated issuer risk weight",
        )
    if cqs is not None:
        rating = number(cqs, "cqs", 1, 6)
        if rating != int(rating):
            raise PfandbriefError("INVALID_RATING", "CQS must be whole")
        value = (0.10, 0.20, 0.20, 0.50, 0.50, 1.0)[int(rating) - 1]
    else:
        rw = number(issuer_risk_weight, "issuer_risk_weight", 0)
        mapping = {
            0.20: 0.10,
            0.30: 0.15,
            0.40: 0.20,
            0.50: 0.25,
            0.75: 0.35,
            1.0: 0.50,
            1.50: 1.0,
        }
        if rw not in mapping:
            raise PfandbriefError(
                "UNMAPPED_RISK_WEIGHT", "issuer risk weight is not in Art129(5)"
            )
        value = mapping[rw]
    return CalcResult(
        value if proof == "MET" else None,
        "covered_bond_risk_weight",
        ("CRR Art129(4)–(7), consolidated2026-06-26",),
        "fraction",
        details={
            "decision": "CHECKS_PASSED"
            if proof == "MET"
            else "INCOMPLETE"
            if proof == "MISSING"
            else "INELIGIBLE",
            "conditional_risk_weight": value,
            "eligibility_status": proof,
        },
        limitations=(
            "No calculation of the issuer risk weight or determination of overall CRR eligibility",
        ),
    )


def european_label(kind, issue_date, *, pfandbrief_status):
    """German PfandBG §41a label conditions, separate from investor risk weights."""
    choice(kind, "kind", KINDS)
    issued = iso_date(issue_date, "issue_date")
    proof = _proof(pfandbrief_status, "pfandbrief_status")
    dated = issued >= iso_date("2022-07-08", "boundary")
    eligible = proof == "MET" and dated
    return CalcResult(
        {"european_covered_bond": eligible, "premium": eligible and kind != "FLG"},
        "european_label",
        ("PfandBG §41a(1)1,(2)1",),
        "classification",
        details={
            "decision": "INCOMPLETE"
            if proof == "MISSING" and dated
            else "CHECKS_PASSED"
            if eligible
            else "INELIGIBLE",
            "kind": kind,
            "issue_date": issued.isoformat(),
        },
        limitations=(
            "Applies to German Pfandbriefe; qualifying foreign instruments require their own supervisory evidence",
        ),
    )


def crr_pool_check(
    assets_nominal,
    bonds_nominal,
    bank_exposures,
    issue_date,
    as_of,
    *,
    eligibility_status,
    required_oc=0.05,
    national_reduction_status="MISSING",
    legacy_status="MISSING",
):
    """Numerical Art129 OC and bank limits for one homogeneous issue-date cohort."""
    assets = number(assets_nominal, "assets_nominal", 0)
    bonds = number(bonds_nominal, "bonds_nominal", 0)
    q = number(required_oc, "required_oc", 0.02)
    issued, day = iso_date(issue_date, "issue_date"), iso_date(as_of, "as_of")
    if issued > day:
        raise PfandbriefError("DATE_ORDER", "issue_date follows as_of")
    proof = _proof(eligibility_status, "eligibility_status")
    national = _proof(national_reduction_status, "national_reduction_status")
    legacy = _proof(legacy_status, "legacy_status")
    old = issued < iso_date("2022-07-08", "boundary")
    ancient = issued < iso_date("2007-12-31", "boundary")
    applied_q = 0.0 if old and legacy == "MET" else q
    fields = (
        "exposure_id",
        "amount",
        "cqs",
        "oc_amount",
        "settlement_amount",
        "category",
        "original_days",
        "approved",
    )
    rows = _records(bank_exposures, fields, "bank_exposures")
    _unique(rows, ("exposure_id",))
    totals = {1: 0.0, 2: 0.0, 3: 0.0}
    oc_sum = 0.0
    numeric = []
    for row in rows:
        amount = number(row["amount"], "amount", 0)
        cqs = number(row["cqs"], "cqs", 1, 3)
        if cqs != int(cqs):
            raise PfandbriefError("INVALID_RATING", "CQS must be whole")
        oc = number(row["oc_amount"], "oc_amount", 0, amount)
        settlement = number(row["settlement_amount"], "settlement_amount", 0, amount)
        if oc + settlement > amount:
            raise PfandbriefError("OVERALLOCATION", "exemptions exceed exposure")
        category = choice(
            row["category"], "category", ("NORMAL", "LIQUIDITY_DEPOSIT", "DERIVATIVE")
        )
        approved = flag(row["approved"], "approved")
        days = row["original_days"]
        if days is not None:
            days = number(days, "original_days", 0)
        if cqs == 3 and not (ancient and legacy == "MET"):
            suitable = (
                category == "LIQUIDITY_DEPOSIT" and days is not None and days <= 100
            ) or (category == "DERIVATIVE" and approved)
            numeric.append(
                {"check": "cqs3_type:" + row["exposure_id"], "passed": suitable}
            )
        totals[int(cqs)] += amount - oc - settlement
        oc_sum += oc
    if oc_sum > applied_q * bonds:
        raise PfandbriefError(
            "OVERALLOCATION", "bank minimum-OC exemption exceeds required OC"
        )
    numeric.append(
        {
            "check": "nominal_oc",
            "passed": assets >= bonds * (1 + applied_q),
            "required": bonds * (1 + applied_q),
            "headroom": assets - bonds * (1 + applied_q),
        }
    )
    if not (ancient and legacy == "MET"):
        for name, amount, ratio in (
            ("cqs1", totals[1], 0.15),
            ("cqs2", totals[2], 0.10),
            ("cqs3", totals[3], 0.08),
            ("cqs_all", sum(totals.values()), 0.15),
            ("cqs2_3", totals[2] + totals[3], 0.10),
        ):
            numeric.append(_limit(name, amount, bonds, ratio, "CRR Art129(1a)"))
    needed = [proof]
    if old:
        needed.append(legacy)
    if applied_q < 0.05 and applied_q > 0:
        needed.append(national)
    decision = (
        "FAILED"
        if not all(r["passed"] for r in numeric) or "NOT_MET" in needed
        else "INCOMPLETE"
        if "MISSING" in needed
        else "CHECKS_PASSED"
    )
    return CalcResult(
        decision,
        "crr_pool_check",
        ("CRR Art129(1),(1a),(3a),(6),(7)",),
        "decision",
        details={
            "checks": numeric,
            "required_oc": applied_q,
            "bank_exposures": {"CQS" + str(k): v for k, v in totals.items()},
            "minimum_oc_exemption": oc_sum,
            "issue_date": issued.isoformat(),
            "as_of": day.isoformat(),
            "legacy_exemption": "PRE_2007"
            if ancient and legacy == "MET"
            else "PRE_2022"
            if old and legacy == "MET"
            else None,
        },
        limitations=(
            "Requires separately evidenced eligible collateral, per-loan limits, Art208/229 valuation and legal qualifications",
            "Issue-date cohorts must be homogeneous; this is not a general RWA calculation",
        ),
    )


def covered_bond_lcr(
    issue_size_eur,
    overcollateralization,
    conditions,
    *,
    cqs=None,
    unrated_risk_weight=None,
    regime="EU",
):
    """LCR covered-bond category candidates; unknown conditions remain visible."""
    size = number(issue_size_eur, "issue_size_eur", 0)
    oc = number(overcollateralization, "overcollateralization", 0)
    choice(regime, "regime", ("EU", "THIRD_COUNTRY"))
    if cqs is not None and unrated_risk_weight is not None:
        raise PfandbriefError(
            "AMBIGUOUS_RATING", "direct rating and unrated risk weight are alternatives"
        )
    if cqs is not None:
        cqs = number(cqs, "cqs", 1, 6)
        if cqs != int(cqs):
            raise PfandbriefError("INVALID_RATING", "CQS must be whole")
    if unrated_risk_weight is not None:
        unrated_risk_weight = number(unrated_risk_weight, "unrated_risk_weight", 0)
    if not isinstance(conditions, dict):
        raise PfandbriefError("INVALID_TABLE", "conditions must be a mapping")
    allowed = {
        "covered_bond_definition",
        "bank_exposures",
        "level2b_collateral",
        "level2b_underlying_rw",
        "monthly_disclosure",
        "third_country_law",
        "equivalent_supervision",
        "third_country_collateral",
        "transparency",
    }
    if set(conditions) - allowed:
        raise PfandbriefError("UNKNOWN_FIELD", "unknown LCR condition")
    for k, v in conditions.items():
        if v is not None:
            flag(v, k)
    candidates = []

    def add(level, haircut, numeric, required):
        missing = [k for k in required if conditions.get(k) is None]
        failed = [k for k in required if conditions.get(k) is False]
        state = "NOT_MET" if not numeric or failed else "MISSING" if missing else "MET"
        candidates.append(
            {
                "level": level,
                "haircut": haircut,
                "status": state,
                "numeric_pass": numeric,
                "missing_conditions": missing,
                "failed_conditions": failed,
            }
        )

    high = cqs == 1 or (cqs is None and unrated_risk_weight == 0.10)
    if regime == "EU":
        common = ("covered_bond_definition", "bank_exposures")
        add("LEVEL1_COVERED", 0.07, size >= 500000000 and high and oc >= 0.02, common)
        better_small = cqs == 1 and size < 500000000
        medium = (
            cqs is not None and cqs <= 2 or cqs is None and unrated_risk_weight == 0.20
        )
        add(
            "LEVEL2A",
            0.15,
            size >= 250000000 and medium and oc >= (0.02 if better_small else 0.07),
            common,
        )
        add(
            "LEVEL2B_COVERED",
            0.30,
            size >= 250000000 and oc >= 0.10,
            (
                "covered_bond_definition",
                "level2b_collateral",
                "level2b_underlying_rw",
                "monthly_disclosure",
            ),
        )
    else:
        add(
            "LEVEL2A",
            0.15,
            high and oc >= (0.02 if size >= 500000000 else 0.07),
            (
                "third_country_law",
                "equivalent_supervision",
                "third_country_collateral",
                "bank_exposures",
                "transparency",
            ),
        )
    selected = next((r for r in candidates if r["status"] == "MET"), None)
    decision = (
        "CHECKS_PASSED"
        if selected
        else "INCOMPLETE"
        if any(r["status"] == "MISSING" for r in candidates)
        else "INELIGIBLE"
    )
    return CalcResult(
        None if selected is None else selected["level"],
        "covered_bond_lcr",
        ("LCR Art10(1)f,(2);11(1)c,d,(2);12(1)e,(2)d",),
        "classification",
        details={
            "decision": decision,
            "minimum_haircut": None if selected is None else selected["haircut"],
            "candidates": candidates,
        },
        limitations=(
            "Conditions are external legal/portfolio assessments; general operational liquidity requirements remain separately evidenced",
            "Uses the explicit locally archived LCR edition; no automatic future-rule substitution",
        ),
    )


def liquid_buffer_value(
    market_value,
    category,
    *,
    qualification_status,
    haircut=None,
    additional_fx_haircut=0,
    as_of=None,
    maturity=None,
):
    """Art9 market-value haircut or <=3-calendar-month qualified bank deposit."""
    value = number(market_value, "market_value", 0)
    proof = _proof(qualification_status, "qualification_status")
    floors = {
        "LEVEL1_OTHER": 0.0,
        "LEVEL1_COVERED": 0.07,
        "LEVEL2A": 0.15,
        "LEVEL2B_COVERED": 0.30,
        "LEVEL2B_OTHER": 0.50,
        "LEVEL2B_SECURITIZATION": None,
        "RESTRICTED_FACILITY": None,
        "BANK_DEPOSIT": 0.0,
    }
    choice(category, "category", floors)
    minimum = floors[category]
    if haircut is None:
        if minimum is None:
            raise PfandbriefError(
                "MISSING_HAIRCUT", "this category needs an explicitly evidenced haircut"
            )
        haircut = minimum
    haircut = number(haircut, "haircut", 0 if minimum is None else minimum, 1)
    additional = number(additional_fx_haircut, "additional_fx_haircut", 0, 1)
    dates_ok = True
    last = None
    if category == "BANK_DEPOSIT":
        day, due = iso_date(as_of, "as_of"), iso_date(maturity, "maturity")
        last = _month_date(day, 3, False)
        dates_ok = day <= due <= last
    elif as_of is not None or maturity is not None:
        raise PfandbriefError(
            "NOT_APPLICABLE", "deposit maturity fields apply only to BANK_DEPOSIT"
        )
    adjusted = value * (1 - haircut) * (1 - additional)
    decision = (
        "INELIGIBLE"
        if proof == "NOT_MET" or not dates_ok
        else "INCOMPLETE"
        if proof == "MISSING"
        else "CHECKS_PASSED"
    )
    return CalcResult(
        adjusted
        if decision == "CHECKS_PASSED"
        else 0.0
        if decision == "INELIGIBLE"
        else None,
        "liquid_buffer_value",
        ("PfandBG §4(1a); LCR Art9–12",),
        "currency",
        details={
            "decision": decision,
            "conditional_value": adjusted,
            "haircut": haircut,
            "additional_fx_haircut": additional,
            "latest_deposit_maturity": None if last is None else last.isoformat(),
        },
        limitations=(
            "Qualification includes asset-specific and general requirements; it is not established by the haircut calculation",
            "No total LCR composition caps are imposed on the Pfandbrief liquidity buffer",
        ),
    )
