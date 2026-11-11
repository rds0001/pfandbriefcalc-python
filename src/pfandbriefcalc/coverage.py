"""Transparent amount arithmetic; full pool qualification is a separate layer.

Copyright 2026 RiskDataScience GmbH. SPDX-License-Identifier: AGPL-3.0-only
"""

from .core import CalcResult, PfandbriefError, number, vector


def secured_amount(
    claim, lien, lending_value, prior_claims, assigned_amount, lending_limit
):
    """Allocate one explicitly established seniority slice; no legal eligibility decision."""
    claim = number(claim, "claim", 0)
    lien = number(lien, "lien", 0)
    value = number(lending_value, "lending_value", 0)
    prior = number(prior_claims, "prior_claims", 0)
    assigned = number(assigned_amount, "assigned_amount", 0)
    limit = number(lending_limit, "lending_limit", 0, 1)
    available = max(0.0, value * limit - prior)
    return CalcResult(
        min(claim, lien, assigned, available),
        "secured_amount",
        ("PfandBG §14; caller-specified seniority and limit",),
        "currency",
        details={"available_rank_slice": available},
        limitations=(
            "Requires separately established eligibility, legal rank and unique allocation",
        ),
    )


def coverage_amounts(assets, liabilities, required_overcollateralization):
    """One homogeneous coverage view; does not certify separate qualifying OC assets."""
    assets = number(assets, "assets", 0)
    liabilities = number(liabilities, "liabilities", 0)
    oc = number(required_overcollateralization, "required_overcollateralization", 0)
    required = liabilities * (1 + oc)
    headroom = assets - required
    return CalcResult(
        headroom,
        "coverage_amounts",
        ("PfandBG §4",),
        "currency",
        details={
            "assets": assets,
            "liabilities": liabilities,
            "required": required,
            "surplus": assets - liabilities,
            "required_extra": liabilities * oc,
            "ratio": None if liabilities == 0 else assets / liabilities,
            "arithmetic_pass": headroom >= 0,
        },
        limitations=(
            "No eligibility, separate OC allocation or overall regulatory approval",
        ),
    )


def liquidity_gap(inflows, outflows, buffer):
    """Worst cumulative daily deficit; vectors contain every day of the chosen horizon."""
    ins, outs = vector(inflows, "inflows", 0), vector(outflows, "outflows", 0)
    buffer = number(buffer, "buffer", 0)
    if not ins or len(ins) != len(outs):
        raise PfandbriefError(
            "LENGTH_MISMATCH", "nonempty daily vectors must have equal length"
        )
    cumulative, balance = [], 0.0
    for inc, out in zip(ins, outs):
        balance += inc - out
        cumulative.append(balance)
    required = max(0.0, -min(cumulative))
    return CalcResult(
        required,
        "liquidity_gap",
        ("PfandBG §4(1a)",),
        "currency",
        details={
            "cumulative": cumulative,
            "buffer": buffer,
            "headroom": buffer - required,
            "arithmetic_pass": buffer >= required,
            "horizon_days": len(ins),
        },
        limitations=(
            "Caller must supply the full regulatory horizon and qualified valued buffer",
        ),
    )
