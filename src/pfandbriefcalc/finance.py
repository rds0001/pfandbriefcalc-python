"""Explicit cashflow and analyst models. SPDX-License-Identifier: AGPL-3.0-only."""

from bisect import bisect_right
import calendar
from datetime import date, timedelta
import math

from .core import CalcResult, PfandbriefError, choice, flag, iso_date, number, vector


def year_fraction(start, end, convention):
    """ACT/365F, ACT/360, 30E/360 or ACT/ACT-ISDA; no implicit convention."""
    a, b = iso_date(start, "start"), iso_date(end, "end")
    choice(convention, "convention", ("ACT/365F", "ACT/360", "30E/360", "ACT/ACT-ISDA"))
    if b < a:
        raise PfandbriefError("DATE_ORDER", "end precedes start")
    if convention in ("ACT/365F", "ACT/360"):
        value = (b - a).days / (365 if convention == "ACT/365F" else 360)
    elif convention == "30E/360":
        value = (
            (b.year - a.year) * 360
            + (b.month - a.month) * 30
            + min(b.day, 30)
            - min(a.day, 30)
        ) / 360
    else:
        value, cursor = 0.0, a
        while cursor < b:
            stop = min(b, date(cursor.year + 1, 1, 1)) if cursor.year < 9999 else b
            value += (stop - cursor).days / (
                366 if calendar.isleap(cursor.year) else 365
            )
            cursor = stop
    return CalcResult(
        value, "year_fraction", unit="years", details={"convention": convention}
    )


def adjust_date(day, convention, holidays):
    """Business date using explicit holidays and Saturday/Sunday weekends."""
    d = iso_date(day, "day")
    choice(
        convention,
        "convention",
        ("unadjusted", "following", "modified_following", "preceding"),
    )
    if isinstance(holidays, (str, bytes, dict)):
        raise PfandbriefError("INVALID_VECTOR", "holidays must be a date sequence")
    try:
        excluded = {iso_date(v, "holiday") for v in holidays}
    except TypeError as exc:
        raise PfandbriefError(
            "INVALID_VECTOR", "holidays must be a date sequence"
        ) from exc

    def valid(x):
        return x.weekday() < 5 and x not in excluded

    value = d
    if convention != "unadjusted":
        step = -1 if convention == "preceding" else 1
        try:
            while not valid(value):
                value += timedelta(days=step)
            if convention == "modified_following" and value.month != d.month:
                value = d
                while not valid(value):
                    value -= timedelta(days=1)
        except OverflowError as exc:
            raise PfandbriefError(
                "DATE_RANGE", "business adjustment exceeds date range"
            ) from exc
    return CalcResult(
        value.isoformat(),
        "adjust_date",
        unit="date",
        details={"convention": convention},
    )


def _month_date(anchor, months, end_of_month):
    total = anchor.year * 12 + anchor.month - 1 + months
    year, month0 = divmod(total, 12)
    if not 1 <= year <= 9999:
        raise PfandbriefError("DATE_RANGE", "schedule exceeds supported date range")
    last = calendar.monthrange(year, month0 + 1)[1]
    return date(year, month0 + 1, last if end_of_month else min(anchor.day, last))


def coupon_schedule(
    start, maturity, frequency, day_count, business_day, holidays, *, end_of_month=False
):
    """Backward anchored schedule with optional short first stub; no adjusted accruals."""
    start, maturity = iso_date(start, "start"), iso_date(maturity, "maturity")
    f = number(frequency, "frequency")
    if f not in (1, 2, 4, 12):
        raise PfandbriefError("OUT_OF_RANGE", "frequency must be 1, 2, 4 or 12")
    flag(end_of_month, "end_of_month")
    if start >= maturity:
        raise PfandbriefError("DATE_ORDER", "maturity must follow start")
    if (
        end_of_month
        and maturity.day != calendar.monthrange(maturity.year, maturity.month)[1]
    ):
        raise PfandbriefError(
            "INCONSISTENT_INPUT", "end_of_month requires month-end maturity"
        )
    boundaries, i = [maturity], 1
    while True:
        candidate = _month_date(maturity, -i * (12 // int(f)), end_of_month)
        if candidate <= start:
            break
        boundaries.append(candidate)
        i += 1
    boundaries.append(start)
    boundaries.reverse()
    # Materialize once so generators cannot silently lose holiday entries.
    try:
        holidays = (
            list(holidays) if not isinstance(holidays, (str, bytes, dict)) else holidays
        )
    except TypeError as exc:
        raise PfandbriefError(
            "INVALID_VECTOR", "holidays must be a date sequence"
        ) from exc
    rows = [
        {
            "start": a.isoformat(),
            "end": b.isoformat(),
            "payment_date": adjust_date(b, business_day, holidays).value,
            "year_fraction": year_fraction(a, b, day_count).value,
        }
        for a, b in zip(boundaries, boundaries[1:])
    ]
    return CalcResult(
        rows,
        "coupon_schedule",
        unit="schedule",
        details={
            "frequency": int(f),
            "day_count": day_count,
            "business_day": business_day,
            "end_of_month": end_of_month,
        },
    )


def contract_cashflows(schedule, principal, coupon_rates, amortizations):
    """Explicit period rates and repayments; remaining principal repaid at maturity."""
    principal = number(principal, "principal", 0)
    rates, amort = (
        vector(coupon_rates, "coupon_rates"),
        vector(amortizations, "amortizations", 0),
    )
    if (
        not isinstance(schedule, (list, tuple))
        or not schedule
        or len(rates) != len(schedule)
        or len(amort) != len(schedule)
    ):
        raise PfandbriefError(
            "LENGTH_MISMATCH", "one rate and repayment required per schedule period"
        )
    rows, balance, previous = [], principal, None
    for i, row in enumerate(schedule):
        if (
            not isinstance(row, dict)
            or not {"start", "end", "payment_date", "year_fraction"} <= row.keys()
        ):
            raise PfandbriefError("MISSING_FIELD", "invalid schedule row")
        a, b, pay = [iso_date(row[k], k) for k in ("start", "end", "payment_date")]
        fraction = number(row["year_fraction"], "year_fraction", 0, strict_min=True)
        if b <= a or pay <= a or (previous is not None and a != previous):
            raise PfandbriefError(
                "DATE_ORDER", "schedule must contain contiguous forward periods"
            )
        if amort[i] > balance:
            raise PfandbriefError(
                "OVERALLOCATION", "repayment exceeds outstanding principal"
            )
        interest = balance * rates[i] * fraction
        redemption = balance if i == len(schedule) - 1 else amort[i]
        rows.append(
            {
                "payment_date": pay.isoformat(),
                "interest": interest,
                "principal": redemption,
                "amount": interest + redemption,
                "opening_balance": balance,
            }
        )
        balance -= redemption
        previous = b
    return CalcResult(
        rows,
        "contract_cashflows",
        unit="currency",
        details={"initial_principal": principal, "terminal_principal": balance},
        limitations=(
            "Rates, resets, option exercise and day-count fractions are explicit contractual inputs",
        ),
    )


def discount_factors(
    times, curve_times, zero_rates, *, extrapolation="error", spread=0.0
):
    """Continuous zero rates; linear zero interpolation; optional explicit flat extrapolation."""
    ts, xs, zs = (
        vector(times, "times", 0),
        vector(curve_times, "curve_times", 0),
        vector(zero_rates, "zero_rates"),
    )
    spread = number(spread, "spread")
    choice(extrapolation, "extrapolation", ("error", "flat_zero"))
    if not xs or len(xs) != len(zs) or any(a >= b for a, b in zip(xs, xs[1:])):
        raise PfandbriefError(
            "INVALID_CURVE",
            "curve nodes must be nonempty, matched and strictly increasing",
        )
    factors, used = [], []
    for t in ts:
        if t == 0:
            z = zs[0]  # DF(0)=1 regardless of the rate; no extrapolation exposure.
        elif t < xs[0] or t > xs[-1]:
            if extrapolation == "error":
                raise PfandbriefError("CURVE_RANGE", "cashflow outside curve range")
            z = zs[0] if t < xs[0] else zs[-1]
        elif t == xs[-1]:
            z = zs[-1]
        else:
            j = bisect_right(xs, t) - 1
            z = zs[j] + (zs[j + 1] - zs[j]) * (t - xs[j]) / (xs[j + 1] - xs[j])
        exponent = -(z + spread) * t
        if not math.isfinite(exponent) or exponent > 709:
            raise PfandbriefError("NUMERIC_RANGE", "discount exponent overflows")
        factors.append(math.exp(exponent))
        used.append(z + spread)
    return CalcResult(
        factors,
        "discount_factors",
        unit="factor",
        details={
            "interpolated_zero_rates": used,
            "extrapolation": extrapolation,
            "compounding": "continuous",
            "interpolation": "linear_zero",
        },
    )


def present_value(
    amounts, times, curve_times, zero_rates, *, extrapolation="error", spread=0.0
):
    """Signed deterministic cashflows in a single currency."""
    cash, ts = vector(amounts, "amounts"), vector(times, "times", 0)
    if not cash or len(cash) != len(ts):
        raise PfandbriefError(
            "LENGTH_MISMATCH", "nonempty matched cashflow vectors required"
        )
    dfs = discount_factors(
        ts, curve_times, zero_rates, extrapolation=extrapolation, spread=spread
    )
    pvs = [a * d for a, d in zip(cash, dfs.value)]
    return CalcResult(
        sum(pvs),
        "present_value",
        ("PfandBarwertV §3; explicit deterministic cashflow model",),
        "currency",
        details={"discount_factors": dfs.value, "cashflow_pvs": pvs},
        limitations=(
            "Does not value embedded options or replace independent derivative market prices",
        ),
    )


def _bond_inputs(amounts, times, frequency):
    cash, ts = vector(amounts, "amounts", 0), vector(times, "times", 0)
    m = number(frequency, "frequency", 0, strict_min=True)
    if not m.is_integer():
        raise PfandbriefError("OUT_OF_RANGE", "frequency must be a positive integer")
    if (
        not cash
        or len(cash) != len(ts)
        or not any(a > 0 and t > 0 for a, t in zip(cash, ts))
    ):
        raise PfandbriefError(
            "INVALID_CASHFLOWS",
            "matched positive future cashflows required for monotone yield",
        )
    return cash, ts, m


def bond_analytics(amounts, times, yield_rate, frequency, *, accrued_interest=0.0):
    """Amount prices, Macaulay/modified duration and convexity; positive cashflows."""
    cash, ts, m = _bond_inputs(amounts, times, frequency)
    y = number(yield_rate, "yield_rate", -m, strict_min=True)
    accrued = number(accrued_interest, "accrued_interest")
    try:
        pv = [a * math.exp(-m * t * math.log1p(y / m)) for a, t in zip(cash, ts)]
    except OverflowError as exc:
        raise PfandbriefError("NUMERIC_RANGE", "yield discount overflows") from exc
    price = sum(pv)
    if not math.isfinite(price) or price <= 0:
        raise PfandbriefError("NUMERIC_RANGE", "price must remain finite and positive")
    mac = sum(t * p for t, p in zip(ts, pv)) / price
    convexity = (
        sum(t * (t + 1 / m) * p for t, p in zip(ts, pv)) / price / (1 + y / m) ** 2
    )
    return CalcResult(
        price,
        "bond_analytics",
        unit="currency",
        details={
            "dirty_price": price,
            "clean_price": price - accrued,
            "macaulay_duration": mac,
            "modified_duration": mac / (1 + y / m),
            "convexity": convexity,
            "frequency": int(m),
            "yield_rate": y,
        },
        limitations=(
            "Deterministic analyst model; prices are amounts, not per-100 quotations",
        ),
    )


def yield_to_maturity(
    price,
    amounts,
    times,
    frequency,
    lower,
    upper,
    *,
    tolerance=1e-12,
    max_iterations=256,
):
    """Bracketed monotone yield solver with explicit bounds and no silent fallback."""
    target = number(price, "price", 0, strict_min=True)
    cash, ts, m = _bond_inputs(amounts, times, frequency)
    lo, hi = (
        number(lower, "lower", -m, strict_min=True),
        number(upper, "upper", -m, strict_min=True),
    )
    tol = number(tolerance, "tolerance", 0, strict_min=True)
    count = number(max_iterations, "max_iterations", 1, 10000)
    if not count.is_integer() or hi <= lo:
        raise PfandbriefError(
            "OUT_OF_RANGE", "ordered bracket and whole iteration count required"
        )

    def price_at(y):
        return bond_analytics(cash, ts, y, m).value

    plo, phi = price_at(lo), price_at(hi)
    if not phi <= target <= plo:
        raise PfandbriefError(
            "NO_BRACKET", "price does not lie within supplied yield bracket"
        )
    for endpoint, p in ((lo, plo), (hi, phi)):
        if p == target:
            return CalcResult(
                endpoint,
                "yield_to_maturity",
                unit="annual_rate",
                details={"iterations": 0, "price_residual": 0.0},
            )
    for i in range(1, int(count) + 1):
        mid = (lo + hi) / 2
        calculated = price_at(mid)
        if hi - lo <= tol or calculated == target:
            return CalcResult(
                mid,
                "yield_to_maturity",
                unit="annual_rate",
                details={"iterations": i, "price_residual": calculated - target},
            )
        if calculated > target:
            lo = mid
        else:
            hi = mid
    raise PfandbriefError("NO_CONVERGENCE", "yield solver exhausted iteration limit")


def accrued_interest(
    principal, coupon_rate, period_start, settlement, period_end, day_count
):
    """Amount accrued from unadjusted coupon start; no ex-coupon convention assumed."""
    n, r = number(principal, "principal", 0), number(coupon_rate, "coupon_rate")
    a, s, b = [
        iso_date(d, "coupon date") for d in (period_start, settlement, period_end)
    ]
    if not a <= s <= b or a == b:
        raise PfandbriefError(
            "DATE_ORDER", "settlement must lie inside a positive coupon period"
        )
    return CalcResult(
        n * r * year_fraction(a, s, day_count).value,
        "accrued_interest",
        unit="currency",
        limitations=("No ex-coupon period or detached-coupon adjustment",),
    )
