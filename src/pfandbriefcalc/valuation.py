"""Atomic lending-value calculations; supplied estimates require separate evidence.

Copyright 2026 RiskDataScience GmbH. SPDX-License-Identifier: AGPL-3.0-only
"""

import math
from .core import CalcResult, PfandbriefError, number, choice

BEL = "BelWertV"


def annuity_factor(rate, years):
    """Annual end-of-period annuity multiplier; rate=0 is a mathematical limit."""
    z = number(rate, "rate", 0)
    n = number(years, "years", 0)
    value = n if z == 0 else -math.expm1(-n * math.log1p(z)) / z
    return CalcResult(
        value,
        "annuity_factor",
        ("BelWertV §12(1)",),
        "years",
        details={"rate": z, "years": n},
        limitations=("No approval of the supplied capitalization rate",),
    )


def income_value(
    net_income,
    land_value,
    rate,
    years,
    *,
    short_life_method=None,
    demolition_costs=None,
    land_release_years=None,
):
    """Income approach including §13 alternatives; returns unrounded monetary value.

    The net income must already include adequate operating-cost deductions.
    For a remaining life below 30 years explicitly select capitalize_land or
    deduct_demolition. Nonpositive building income requires land_release_years.
    """
    n_income = number(net_income, "net_income")
    land = number(land_value, "land_value", 0)
    z = number(rate, "rate", 0, strict_min=True)
    years = number(years, "years", 0)
    if short_life_method is not None:
        choice(
            short_life_method,
            "short_life_method",
            ("capitalize_land", "deduct_demolition"),
        )
    if demolition_costs is not None:
        demolition_costs = number(demolition_costs, "demolition_costs", 0)
    if land_release_years is not None:
        land_release_years = number(land_release_years, "land_release_years", 0)
    factor = annuity_factor(z, years).value
    building_income = n_income - land * z
    branch, demolition_pv = "standard", 0.0
    if building_income <= 0:
        if demolition_costs is None or land_release_years is None:
            raise PfandbriefError(
                "MISSING_INPUT",
                "§13(1) requires demolition_costs and land_release_years",
            )
        value = (land - demolition_costs) * math.exp(
            -land_release_years * math.log1p(z)
        )
        branch = "land_only_discounted"
    elif years < 30:
        if short_life_method is None:
            raise PfandbriefError(
                "MISSING_METHOD", "§13(2) requires an explicit short-life alternative"
            )
        branch = short_life_method
        if branch == "capitalize_land":
            value = n_income * factor
        else:
            if demolition_costs is None or land_release_years is None:
                raise PfandbriefError(
                    "MISSING_INPUT",
                    "demolition alternative needs amount and release time",
                )
            demolition_pv = demolition_costs * math.exp(
                -land_release_years * math.log1p(z)
            )
            value = land + building_income * factor - demolition_pv
    else:
        if short_life_method is not None:
            raise PfandbriefError(
                "NOT_APPLICABLE", "short-life alternative is restricted to years < 30"
            )
        value = land + building_income * factor
    return CalcResult(
        value,
        "income_value",
        ("BelWertV §§8–13",),
        "currency",
        details={
            "branch": branch,
            "annuity_factor": factor,
            "building_income": building_income,
            "demolition_pv": demolition_pv,
            "land_share_review_required": land > value / 2,
        },
        limitations=(
            "Rate, net income, land estimate and valuation evidence are supplied inputs",
            "Not a binding lending-value determination",
        ),
    )


def comparison_value(base_value, haircut=0.10):
    """Apply the §19 minimum haircut to an independently established comparison value."""
    base = number(base_value, "base_value", 0)
    h = number(haircut, "haircut", 0.10, 1)
    if h == 1:
        raise PfandbriefError("OUT_OF_RANGE", "haircut must be less than one")
    return CalcResult(
        base * (1 - h),
        "comparison_value",
        ("BelWertV §19",),
        "currency",
        details={"base_value": base, "haircut": h},
        limitations=(
            "Comparable selection and adjustments require independent evidence",
        ),
    )


def cost_value(
    construction_value,
    land_value,
    age_depreciation,
    *,
    safety_haircut=0.10,
    incidental_rate=0.0,
    other_deductions=0.0,
    demolition_present_value=0.0,
):
    """Cost-value arithmetic with explicit depreciation and separately assessed deductions."""
    construction = number(construction_value, "construction_value", 0)
    land = number(land_value, "land_value", 0)
    age = number(age_depreciation, "age_depreciation", 0, 1)
    haircut = number(safety_haircut, "safety_haircut", 0.10, 1)
    incidental = number(incidental_rate, "incidental_rate", 0, 0.20)
    deductions = number(other_deductions, "other_deductions", 0)
    demolition = number(demolition_present_value, "demolition_present_value", 0)
    reduced = construction * (1 - haircut)
    building = reduced * (1 + incidental) * (1 - age)
    return CalcResult(
        land + building - deductions - demolition,
        "cost_value",
        ("BelWertV §§14–17",),
        "currency",
        details={
            "reduced_construction_value": reduced,
            "building_value": building,
            "incidental_before_age": reduced * incidental,
        },
        limitations=(
            "§14 demolition assessment for short remaining life remains required",
            "Explicit depreciation must follow the documented age model",
        ),
    )


def _history(years, average):
    years = number(years, "history_years", 0, 10)
    if not years.is_integer():
        raise PfandbriefError(
            "OUT_OF_RANGE", "history_years must be whole calendar years"
        )
    if average is not None:
        average = number(average, "average_market_value", 0)
        if years == 0:
            raise PfandbriefError(
                "INCONSISTENT_INPUT", "average requires positive history_years"
            )
    elif years != 0:
        raise PfandbriefError(
            "INCONSISTENT_INPUT", "missing average requires history_years=0"
        )
    return years, average


def ship_value_limit(
    current_market_value,
    average_market_value,
    price,
    history_years,
    *,
    extra_haircut=0.0,
):
    """Ship value upper bound; not the valuation or approval of an alternative method."""
    years, average = _history(history_years, average_market_value)
    price = number(price, "price", 0)
    extra = number(extra_haircut, "extra_haircut", 0, 1)
    current = (
        None
        if current_market_value is None
        else number(current_market_value, "current_market_value", 0)
    )
    if current is None or average is None:
        haircut = max(0.25, extra)
        caps = {"price_adjusted": price * (1 - haircut)}
        alternative = True
    else:
        haircut = max(extra, 0 if years == 10 else (0.25 if years <= 3 else 0.15))
        caps = {
            "current_adjusted": current * (1 - haircut),
            "average": average,
            "price": price,
        }
        alternative = False
    return CalcResult(
        min(caps.values()),
        "ship_value_limit",
        ("SchiffsBelWertV §4",),
        "currency",
        details={
            "caps": caps,
            "haircut": haircut,
            "alternative_method_required": alternative,
        },
        limitations=(
            "Upper limit only; a sustainable appraised value must be established separately",
        ),
    )


def aircraft_value_limit(
    current_market_value, average_market_value, balanced_value, history_years
):
    """Aircraft upper limits, preserving available independent bounds."""
    years, average = _history(history_years, average_market_value)
    balanced = number(balanced_value, "balanced_value", 0)
    current = (
        None
        if current_market_value is None
        else number(current_market_value, "current_market_value", 0)
    )
    caps = {"balanced_adjusted": balanced * (0.90 if years < 10 else 1)}
    if average is not None:
        caps["average"] = average
    if current is not None:
        caps["current"] = current
    else:
        caps["alternative_balanced_cap"] = balanced * 0.75
    return CalcResult(
        min(caps.values()),
        "aircraft_value_limit",
        ("FlugBelWertV §4",),
        "currency",
        details={"caps": caps, "alternative_method_required": current is None},
        limitations=(
            "Upper limit only; estimates, sustainable value and method evidence are external",
        ),
    )
