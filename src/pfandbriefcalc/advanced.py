"""Explicit curve analytics and additional lending-value methods.

Copyright 2026 RiskDataScience GmbH. SPDX-License-Identifier: AGPL-3.0-only
"""

from .core import CalcResult, PfandbriefError, number, vector, choice
from .finance import present_value, discount_factors
from .stress import rate_shocks
from .valuation import income_value
from .property import valuation_review
from .eu import _proof


def cashflow_scenarios(
    amounts,
    times,
    curve_times,
    zero_rates,
    *,
    method,
    history=None,
    ddof=1,
    extrapolation="error",
    spread=0,
):
    """Three valuations of fixed linear cashflows; FX is a separate currency-net step."""
    shifts = rate_shocks(
        zero_rates,
        method=method,
        tenors=curve_times if method == "dynamic" else None,
        history=history,
        ddof=ddof,
    )
    results = {}
    for scenario, rates in (
        ("BASE", zero_rates),
        ("UP", shifts.details["up"]),
        ("DOWN", shifts.details["down"]),
    ):
        results[scenario] = present_value(
            amounts,
            times,
            curve_times,
            rates,
            extrapolation=extrapolation,
            spread=spread,
        )
    return CalcResult(
        {k: v.value for k, v in results.items()},
        "cashflow_scenarios",
        ("PfandBarwertV §§3–5; fixed linear cashflow model",),
        "currency",
        details={
            "shock": shifts.as_dict(),
            "valuations": {k: v.as_dict() for k, v in results.items()},
        },
        limitations=(
            "Fixed amounts are not reprojected under stress; floating coupons must be reprojected separately",
            "Not an embedded-option model or independent derivative market price",
        ),
    )


def project_floating_coupons(
    reset_times,
    start_times,
    end_times,
    accrual_fractions,
    fixings,
    curve_times,
    zero_rates,
    *,
    margin=0,
    floor=None,
    cap=None,
    bound_on="all_in",
    extrapolation="error",
):
    """In-advance simple forward coupons with explicit historical fixings and bound basis."""
    resets = vector(reset_times, "reset_times")
    starts = vector(start_times, "start_times")
    ends = vector(end_times, "end_times")
    fractions = vector(accrual_fractions, "accrual_fractions", 0)
    if (
        not isinstance(fixings, (list, tuple))
        or not resets
        or len({len(resets), len(starts), len(ends), len(fractions), len(fixings)}) != 1
    ):
        raise PfandbriefError(
            "LENGTH_MISMATCH",
            "all coupon-period vectors must have the same nonzero length",
        )
    margin = number(margin, "margin")
    choice(bound_on, "bound_on", ("index", "all_in"))
    if floor is not None:
        floor = number(floor, "floor")
    if cap is not None:
        cap = number(cap, "cap")
    if floor is not None and cap is not None and floor > cap:
        raise PfandbriefError("INVALID_BOUNDS", "floor exceeds cap")
    rates, rows = [], []
    for i, (reset, start, end, fraction, fixing) in enumerate(
        zip(resets, starts, ends, fractions, fixings)
    ):
        if end <= start or fraction <= 0 or reset > start:
            raise PfandbriefError(
                "INVALID_PERIOD", "require positive period/accrual and in-advance reset"
            )
        if reset <= 0:
            if fixing is None:
                raise PfandbriefError(
                    "MISSING_FIXING", "past/current reset needs an actual fixing"
                )
            index, origin = number(fixing, "fixing"), "FIXED"
        else:
            if fixing is not None:
                raise PfandbriefError(
                    "FUTURE_FIXING",
                    "future reset must be projected, not assigned a historical fixing",
                )
            df = discount_factors(
                [start, end], curve_times, zero_rates, extrapolation=extrapolation
            ).value
            if df[1] == 0:
                raise PfandbriefError(
                    "NUMERIC_RANGE", "zero forward discount denominator"
                )
            index, origin = (df[0] / df[1] - 1) / fraction, "PROJECTED"
        raw = index if bound_on == "index" else index + margin
        bounded = max(raw, floor) if floor is not None else raw
        bounded = min(bounded, cap) if cap is not None else bounded
        coupon = bounded + margin if bound_on == "index" else bounded
        rates.append(coupon)
        rows.append(
            {
                "period": i + 1,
                "origin": origin,
                "index_rate": index,
                "coupon_rate": coupon,
            }
        )
    return CalcResult(
        rates,
        "project_floating_coupons",
        unit="decimal_rate",
        details={"periods": rows, "bound_on": bound_on},
        limitations=(
            "Projection curve and coupon day fractions are explicit inputs; no option time value or in-arrears convexity model",
        ),
    )


def effective_sensitivities(
    amounts,
    times,
    curve_times,
    zero_rates,
    *,
    bump=0.0001,
    spread=0,
    extrapolation="error",
):
    """Parallel continuous-zero-rate finite differences; separate from statutory stress."""
    step = number(bump, "bump", 0, strict_min=True)
    rates = vector(zero_rates, "zero_rates")
    values = [
        present_value(
            amounts,
            times,
            curve_times,
            [r + s for r in rates],
            extrapolation=extrapolation,
            spread=spread,
        ).value
        for s in (0, -step, step)
    ]
    base, down, up = values
    if base == 0:
        raise PfandbriefError(
            "ZERO_PRICE", "relative sensitivity needs a nonzero base value"
        )
    duration = (down - up) / (2 * base * step)
    convexity = (down + up - 2 * base) / (base * step * step)
    return CalcResult(
        {
            "present_value": base,
            "effective_duration": duration,
            "effective_convexity": convexity,
            "dv01": (down - up) / (2 * step) * 0.0001,
        },
        "effective_sensitivities",
        unit="mixed",
        details={
            "bump": step,
            "down_value": down,
            "up_value": up,
            "model": "fixed cashflows, continuous zero curve parallel shift",
        },
        limitations=(
            "Signed offsetting cashflows may make relative measures unstable; this is not a regulatory stress decision",
        ),
    )


def equivalent_cap_rate(
    net_income,
    target_value,
    land_value,
    years,
    lower,
    upper,
    *,
    short_life_method=None,
    tolerance=1e-10,
    max_iterations=256,
):
    """Find an explicitly bounded result-equivalent capitalization rate, BelWertV §25(5)."""
    income = number(net_income, "net_income", 0, strict_min=True)
    target = number(target_value, "target_value", 0, strict_min=True)
    land = number(land_value, "land_value", 0)
    low = number(lower, "lower", 0, strict_min=True)
    high = number(upper, "upper", low, strict_min=True)
    tol = number(tolerance, "tolerance", 0, strict_min=True)
    count = number(max_iterations, "max_iterations", 1)
    if count != int(count):
        raise PfandbriefError("OUT_OF_RANGE", "max_iterations must be whole")
    if years is None:
        if short_life_method is not None:
            raise PfandbriefError(
                "NOT_APPLICABLE", "perpetuity takes no short-life method"
            )
        rate = income / target
        if not low <= rate <= high:
            raise PfandbriefError(
                "NO_BRACKET", "equivalent rate is outside supplied bounds"
            )
        return CalcResult(
            rate,
            "equivalent_cap_rate",
            ("BelWertV §25(5); explicit perpetuity convention",),
            "decimal_rate",
            details={
                "target_value": target,
                "reproduced_value": income / rate,
                "iterations": 0,
            },
        )
    life = number(years, "years", 0, strict_min=True)
    if life < 30:
        choice(short_life_method, "short_life_method", ("capitalize_land",))
    elif short_life_method is not None:
        raise PfandbriefError(
            "NOT_APPLICABLE", "short-life method applies only below30years"
        )
    if income - land * high <= 0:
        raise PfandbriefError(
            "METHOD_DOMAIN", "bracket must keep building income positive"
        )

    def value(rate):
        return income_value(
            income, land, rate, life, short_life_method=short_life_method
        ).value

    if not value(high) <= target <= value(low):
        raise PfandbriefError(
            "NO_BRACKET", "target value is outside supplied rate bracket"
        )
    for iteration in range(1, int(count) + 1):
        rate = (low + high) / 2
        actual = value(rate)
        if abs(actual - target) <= tol * max(1.0, target):
            return CalcResult(
                rate,
                "equivalent_cap_rate",
                ("BelWertV §25(5); income-value result equivalence",),
                "decimal_rate",
                details={
                    "target_value": target,
                    "reproduced_value": actual,
                    "iterations": iteration,
                },
                limitations=(
                    "Target value must independently include required costs; no method eligibility is inferred",
                ),
            )
        if actual > target:
            low = rate
        else:
            high = rate
    raise PfandbriefError("NO_CONVERGENCE", "equivalent-rate solver did not converge")


def ship_construction_value_check(
    proposed_value, confirmed_state_value, market_value, *, confirmation_status
):
    """Compare a proposed value to the externally confirmed construction-state value."""
    proposed = number(proposed_value, "proposed_value", 0)
    state = number(confirmed_state_value, "confirmed_state_value", 0)
    market = number(market_value, "market_value", 0)
    proof = _proof(confirmation_status, "confirmation_status")
    maximum = min(state, market)
    decision = (
        "FAILED"
        if proposed > maximum or proof == "NOT_MET"
        else "INCOMPLETE"
        if proof == "MISSING"
        else "CHECKS_PASSED"
    )
    return CalcResult(
        decision,
        "ship_construction_value_check",
        ("SchiffsBelWertV §13; PfandBG §24",),
        "decision",
        details={"maximum": maximum, "headroom": maximum - proposed},
        limitations=(
            "State value and construction progress must be confirmed by the yard or technical expert; no statutory linear-progress formula is assumed",
        ),
    )


def transport_valuation_review(
    kind, as_of, last_monitoring, material_deterioration, material_arrears_days
):
    """Annual ship/aircraft monitoring and deterioration/90-day arrears review triggers."""
    choice(kind, "kind", ("SCH", "FLG"))
    result = valuation_review(
        as_of, last_monitoring, material_deterioration, material_arrears_days
    )
    return CalcResult(
        result.value,
        "transport_valuation_review",
        ("SchiffsBelWertV §14" if kind == "SCH" else "FlugBelWertV §12",),
        "boolean",
        details=result.details,
        limitations=result.limitations,
    )
