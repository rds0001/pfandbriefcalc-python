"""Quantitative eligibility and derived external-evidence requirements.

Copyright 2026 RiskDataScience GmbH. SPDX-License-Identifier: AGPL-3.0-only
"""

import calendar
from datetime import date
from .core import CalcResult, PfandbriefError, number, choice, flag, vector, iso_date
from .controls import _text
from .coverage import secured_amount
from .pools import KINDS


def _years(day, count):
    year = day.year + count
    if not 1 <= year <= 9999:
        raise PfandbriefError("DATE_RANGE", "calendar year is out of range")
    return date(year, day.month, min(day.day, calendar.monthrange(year, day.month)[1]))


def cover_amount(
    category,
    claim,
    registered,
    redemption,
    *,
    defaulted,
    guaranteed,
    guarantor_defaulted,
    lien=None,
    lending_value=None,
    prior_claims=None,
    guarantee_amount=None,
    lending_limit=0.60,
):
    """Nominal upper bound after rank, redemption and explicit default treatment."""
    choice(
        category, "category", ("MORTGAGE", "PUBLIC", "SHIP", "AIRCRAFT", "SUBSTITUTE")
    )
    claim = number(claim, "claim", 0)
    assigned = number(registered, "registered", 0)
    redemption = number(redemption, "redemption", 0)
    default = flag(defaulted, "defaulted")
    guarantee = flag(guaranteed, "guaranteed")
    gd = flag(guarantor_defaulted, "guarantor_defaulted")
    limit = number(lending_limit, "lending_limit", 0, 1)
    secured = category in ("MORTGAGE", "SHIP", "AIRCRAFT")
    excluded = (gd and guarantee) or (default and not secured and not guarantee)
    if gd and not guarantee:
        raise PfandbriefError(
            "NOT_APPLICABLE", "guarantor default requires a guarantee"
        )
    amount = min(claim, assigned, redemption)
    rank_capacity = None
    if secured:
        result = secured_amount(
            claim, lien, lending_value, prior_claims, assigned, limit
        )
        amount = min(amount, result.value)
        rank_capacity = result.details["available_rank_slice"]
    elif any(x is not None for x in (lien, lending_value, prior_claims)):
        raise PfandbriefError(
            "NOT_APPLICABLE", "nonsecured category takes no collateral inputs"
        )
    if guarantee:
        amount = min(amount, number(guarantee_amount, "guarantee_amount", 0))
    elif guarantee_amount is not None:
        raise PfandbriefError("NOT_APPLICABLE", "guarantee amount requires a guarantee")
    return CalcResult(
        0.0 if excluded else amount,
        "cover_amount",
        ("PfandBG §§4(2),(4),14,20,22,26b",),
        "currency",
        details={
            "category": category,
            "before_default_exclusion": amount,
            "default_excluded": excluded,
            "rank_capacity": rank_capacity,
            "lending_limit": limit if secured else None,
        },
        limitations=(
            "External eligibility, prior/equal rank allocation and the value appraisal remain prerequisites",
            "Any lending-limit departure from .60 requires an applicable evidenced exception/profile",
        ),
    )


def mortgage_terms_check(
    country_group,
    maturity,
    *,
    permanent_income,
    construction_or_land,
    right_expiry=None,
    economic_end=None,
):
    """Permitted location group and fixed-term-right calendar boundaries."""
    group = choice(
        country_group,
        "country_group",
        ("EU_EEA", "CH", "GB", "US", "CA", "JP", "AU", "NZ", "SG", "OTHER"),
    )
    end = iso_date(maturity, "maturity")
    income = flag(permanent_income, "permanent_income")
    building = flag(construction_or_land, "construction_or_land")
    checks = {
        "location": group != "OTHER",
        "income_or_construction": income or building,
    }
    last = None
    if right_expiry is not None:
        expiry = iso_date(right_expiry, "right_expiry")
        economic = iso_date(economic_end, "economic_end")
        last = min(_years(expiry, -10), economic)
        checks["fixed_term_right"] = end <= last
    elif economic_end is not None:
        raise PfandbriefError(
            "NOT_APPLICABLE", "economic_end here applies to a fixed-term right"
        )
    return CalcResult(
        "CHECKS_PASSED" if all(checks.values()) else "FAILED",
        "mortgage_terms_check",
        ("PfandBG §§13,16(3)",),
        "decision",
        details={
            "checks": checks,
            "latest_maturity": None if last is None else last.isoformat(),
        },
        limitations=(
            "Country membership, comparable legal rights and lasting income require evidence",
        ),
    )


def transport_loan_check(
    kind,
    loan_amount,
    annual_amortizations,
    balloon,
    age_at_maturity,
    expected_life,
    defer_years,
    *,
    maturity_exception=False,
    repayment_exception=False,
    defer_exception=False,
    extended_forbearance=False,
    trustee_consent=False,
    reconciliation_tolerance=1e-8,
):
    """Annual amortization, permitted balloon, life and deferral checks for SCH/FLG."""
    choice(kind, "kind", ("SCH", "FLG"))
    principal = number(loan_amount, "loan_amount", 0)
    payments = vector(annual_amortizations, "annual_amortizations", 0)
    if not payments:
        raise PfandbriefError(
            "EMPTY_SCHEDULE", "provide annual regular repayments excluding balloon"
        )
    balloon = number(balloon, "balloon", 0)
    age = number(age_at_maturity, "age_at_maturity", 0)
    life = number(expected_life, "expected_life", 0, strict_min=True)
    delay = number(defer_years, "defer_years", 0)
    for name, value in (
        ("maturity_exception", maturity_exception),
        ("repayment_exception", repayment_exception),
        ("defer_exception", defer_exception),
        ("extended_forbearance", extended_forbearance),
        ("trustee_consent", trustee_consent),
    ):
        flag(value, name)
    tolerance = number(reconciliation_tolerance, "reconciliation_tolerance", 0)
    uniform = all(x == payments[0] for x in payments)
    decreasing = all(a >= b for a, b in zip(payments, payments[1:]))
    capacity = payments[0] * max(0.0, 20 - age) if uniform else 0.0
    checks = {
        "principal_reconciles": abs(sum(payments) + balloon - principal) <= tolerance,
        "amortization_pattern": decreasing or repayment_exception,
        "balloon": balloon == 0
        or (uniform and balloon <= capacity)
        or repayment_exception,
        "maturity": age <= min(20.0, life)
        or maturity_exception
        or (extended_forbearance and trustee_consent),
        "deferral": delay <= (5.0 if defer_exception else 2.0),
        "trustee_forbearance": not extended_forbearance or trustee_consent,
    }
    required = [
        name
        for name, value in (
            ("maturity_exception", maturity_exception),
            ("repayment_exception", repayment_exception),
            ("defer_exception", defer_exception),
            ("trustee_consent", extended_forbearance),
        )
        if value
    ]
    return CalcResult(
        "CHECKS_PASSED" if all(checks.values()) else "FAILED",
        "transport_loan_check",
        ("PfandBG §§22,25,26b,26e",),
        "decision",
        details={
            "checks": checks,
            "balloon_capacity": capacity,
            "regular_amortizations": payments,
            "regular_plus_balloon": sum(payments) + balloon,
            "required_approval_evidence": required,
        },
        limitations=(
            "Annual repayments exclude the final balloon; exceptions and consent need separate dated evidence",
        ),
    )


def insurance_check(
    kind,
    insured_amount,
    claim,
    *,
    prior_equal_claims=0,
    basis=None,
    reconstruction_cost=None,
    probable_maximum_loss=None,
    current_value_loss=None,
):
    """Amount test only; rights, insured risks and notices remain separate evidence."""
    choice(kind, "kind", ("HYP", "SCH", "FLG"))
    insured = number(insured_amount, "insured_amount", 0)
    claim = number(claim, "claim", 0)
    prior = number(prior_equal_claims, "prior_equal_claims", 0)
    if kind == "HYP":
        choice(
            basis,
            "basis",
            ("reconstruction", "probable_maximum_loss", "claim_current_value"),
        )
        if prior:
            raise PfandbriefError(
                "NOT_APPLICABLE",
                "HYP insurance amount test takes no transport prior-right amount",
            )
        selected = {
            "reconstruction": reconstruction_cost,
            "probable_maximum_loss": probable_maximum_loss,
            "claim_current_value": current_value_loss,
        }
        for key, value in selected.items():
            if key != basis and value is not None:
                raise PfandbriefError(
                    "NOT_APPLICABLE", "supply only the selected insurance basis"
                )
        required = number(selected[basis], basis, 0)
        if basis == "claim_current_value":
            required = min(claim, required)
    else:
        if any(
            v is not None
            for v in (
                basis,
                reconstruction_cost,
                probable_maximum_loss,
                current_value_loss,
            )
        ):
            raise PfandbriefError(
                "NOT_APPLICABLE",
                "transport insurance uses claim and prior/equal third-party rights",
            )
        required = claim + claim * 0.10 + prior
    return CalcResult(
        "CHECKS_PASSED" if insured >= required else "FAILED",
        "insurance_check",
        ("PfandBG §§15,23,26c",),
        "decision",
        details={
            "required": required,
            "insured_amount": insured,
            "headroom": insured - required,
            "basis": basis,
        },
        limitations=(
            "Transport formula: 110% of own outstanding claim plus prior/equal third-party rights",
            "Does not establish insured risks, legal entitlement, notices or annual loss-cap validity",
        ),
    )


def required_evidence(kind, position_id, category, features=()):
    """Derive a nonempty evidence contract from position category and explicit features."""
    choice(kind, "kind", KINDS)
    scope = _text(position_id, "position_id")
    choice(
        category,
        "category",
        ("MORTGAGE", "PUBLIC", "SHIP", "AIRCRAFT", "SUBSTITUTE", "DERIVATIVE", "BOND"),
    )
    expected = {"MORTGAGE": "HYP", "PUBLIC": "OEF", "SHIP": "SCH", "AIRCRAFT": "FLG"}
    if category in expected and expected[category] != kind:
        raise PfandbriefError(
            "KIND_MISMATCH", "primary category does not match the Pfandbrief kind"
        )
    allowed = (
        "foreign",
        "partial",
        "refinancing",
        "guaranteed",
        "pv_oc",
        "liquidity",
        "legacy",
        "exception",
        "own_held",
        "payment_settlement",
    )
    if not isinstance(features, (list, tuple)) or any(
        f not in allowed for f in features
    ):
        raise PfandbriefError("INVALID_FEATURE", "unknown evidence feature")
    if len(set(features)) != len(features):
        raise PfandbriefError("DUPLICATE_KEY", "duplicate evidence feature")
    reqs = {
        "registration_allocation": "PfandBG §5; DeckRegV §§8–14",
        "claim_enforceability": "PfandBG §§12–26f",
    }
    if category == "BOND":
        reqs = {
            "bond_outstanding": "PfandBG §4(5); §8(3)",
            "bond_terms": "PfandBG §§4(2),6",
        }
    else:
        reqs.update(
            default_assessment="PfandBG §4(4)",
            limit_classification="PfandBG §§13,19,20,22,26,26b,26f",
        )
    if category in ("MORTGAGE", "SHIP", "AIRCRAFT"):
        reqs.update(
            valuation="PfandBG §§16,24,26d; applicable lending-value ordinance",
            independent_valuer="PfandBG §§16(1),24(1),26d(1)",
            valuation_monitoring="BelWertV §26; SchiffsBelWertV §14; FlugBelWertV §12",
            security_rank="PfandBG §§12–14,18,22,26b",
            insurance="PfandBG §§15,23,26c",
            primary_conditions="PfandBG §§13,16(3),22,25,26b,26e",
        )
    if category == "AIRCRAFT":
        reqs["engines_reregistration"] = "PfandBG §26b(2)"
    if category == "PUBLIC":
        reqs["public_debtor_category"] = "PfandBG §20(1)"
    if category == "SUBSTITUTE":
        reqs["substitute_eligibility"] = "PfandBG §§4(1),19,20,26,26f"
    if category == "DERIVATIVE":
        reqs.update(
            derivative_framework="PfandBG §4b(1)",
            hedge_relationship="PfandBG §4b(1)–(2)",
            insolvency_protection="PfandBG §4b(1)",
            counterparty="PfandBG §4b(4)–(6)",
            independent_market_values="PfandBarwertV §3(1)",
        )
    feature_refs = {
        "foreign": "PfandBG §§13,18,20(3),22(5),26b(4)",
        "partial": "PfandBG §5(1a); DeckRegV §9(7)",
        "refinancing": "PfandBG §1(2); DeckRegV §9(6); RefiRegV",
        "guaranteed": "PfandBG §20(1)2",
        "pv_oc": "PfandBG §4(1) sentence3",
        "liquidity": "PfandBG §4(1a); LCR Art9–12",
        "legacy": "PfandBG §§45–55; applicable transition",
        "exception": "Applicable individual statutory permission",
        "own_held": "PfandBG §4(5)",
        "payment_settlement": "PfandBG §19(1) sentence6",
    }
    for feature in features:
        reqs["feature_" + feature] = feature_refs[feature]
    return CalcResult(
        [
            {
                "requirement_id": key,
                "scope": scope,
                "allow_not_applicable": key == "insurance" and category == "MORTGAGE",
                "source_ref": value,
            }
            for key, value in reqs.items()
        ],
        "required_evidence",
        tuple(sorted(set(reqs.values()))),
        "records",
        details={"kind": kind, "category": category, "features": list(features)},
        limitations=(
            "Requires truthful position classification; presence of evidence does not authenticate its conclusion",
        ),
    )
