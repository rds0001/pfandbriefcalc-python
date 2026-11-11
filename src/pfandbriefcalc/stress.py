"""PfandBarwertV shock arithmetic. SPDX-License-Identifier: AGPL-3.0-only."""

import math
from .core import CalcResult, PfandbriefError, choice, number, vector


def _sd(values, ddof):
    ddof = number(ddof, "ddof", 0, 1)
    if ddof not in (0, 1):
        raise PfandbriefError("OUT_OF_RANGE", "ddof must be zero or one")
    mean = sum(values) / len(values)
    return math.sqrt(sum((x - mean) ** 2 for x in values) / (len(values) - ddof))


def rate_shocks(current_rates, *, method, tenors=None, history=None, ddof=1):
    """Decimal up/down shocks. Dynamic history: 250 rows, columns correspond to tenors."""
    current = vector(current_rates, "current_rates")
    if not current:
        raise PfandbriefError("INVALID_CURVE", "current curve must not be empty")
    choice(method, "method", ("static", "dynamic"))
    if method == "static":
        if history is not None or tenors is not None:
            raise PfandbriefError(
                "NOT_APPLICABLE", "static stress takes no historical curve"
            )
        shifts, mode = [0.025] * len(current), "static"
    else:
        tenors = vector(tenors, "tenors", 0)
        if len(tenors) != len(current) or any(
            a >= b for a, b in zip(tenors, tenors[1:])
        ):
            raise PfandbriefError(
                "INVALID_CURVE", "ordered tenors must match current rates"
            )
        if not all(
            any(abs(x - r) < 1e-10 for x in tenors)
            for r in (1 / 12, 1, 2, 5, 7, 10, 15)
        ):
            raise PfandbriefError(
                "MISSING_TENOR", "dynamic stress requires all seven statutory tenors"
            )
        if not isinstance(history, (list, tuple)) or len(history) != 250:
            raise PfandbriefError(
                "HISTORY_LENGTH", "250 historical curve observations required"
            )
        rows = [vector(row, "history row") for row in history]
        if any(len(row) != len(current) for row in rows):
            raise PfandbriefError(
                "LENGTH_MISMATCH", "history columns must match current curve"
            )
        absolute = any(x <= 0 for row in rows for x in row)
        mode = "absolute_changes" if absolute else "log_changes"
        shifts = []
        for j, level in enumerate(current):
            observations = [row[j] if absolute else math.log(row[j]) for row in rows]
            changes = [b - a for a, b in zip(observations, observations[1:])]
            raw = (
                _sd(changes, ddof) * 2.33 * math.sqrt(125) * (1 if absolute else level)
            )
            shifts.append(max(0.01, raw))
    return CalcResult(
        shifts,
        "rate_shocks",
        ("PfandBarwertV §5",),
        "decimal_rate",
        details={
            "mode": mode,
            "up": [x + s for x, s in zip(current, shifts)],
            "down": [x - s for x, s in zip(current, shifts)],
            "ddof": ddof,
            "history_observations": 250 if method == "dynamic" else 0,
        },
        limitations=(
            "Historical bank-day calendar, method continuity and approvals require evidence",
        ),
    )


def fx_shock(*, method, currency_group=None, history=None, other_haircut=None, ddof=1):
    """Relative FX shock. Explicit country group; no built-in mutable country list."""
    choice(method, "method", ("static", "dynamic"))
    if method == "static":
        if history is not None:
            raise PfandbriefError("NOT_APPLICABLE", "static FX stress takes no history")
        choice(currency_group, "currency_group", ("EU_EEA_CH", "US_CA_UK_JP", "OTHER"))
        if currency_group == "OTHER":
            shock = number(other_haircut, "other_haircut", 0.25)
        else:
            if other_haircut is not None:
                raise PfandbriefError(
                    "NOT_APPLICABLE", "other_haircut applies only to OTHER"
                )
            shock = 0.10 if currency_group == "EU_EEA_CH" else 0.20
    else:
        if currency_group is not None or other_haircut is not None:
            raise PfandbriefError(
                "NOT_APPLICABLE", "dynamic FX stress takes no static class"
            )
        levels = vector(history, "history", 0)
        if len(levels) != 250:
            raise PfandbriefError(
                "HISTORY_LENGTH", "250 historical FX observations required"
            )
        if any(v == 0 for v in levels):
            raise PfandbriefError("OUT_OF_RANGE", "FX observations must be positive")
        logs = [math.log(v) for v in levels]
        shock = (
            _sd([b - a for a, b in zip(logs, logs[1:])], ddof) * 2.33 * math.sqrt(125)
        )
    return CalcResult(
        shock,
        "fx_shock",
        ("PfandBarwertV §6",),
        "fraction",
        details={"method": method, "currency_group": currency_group, "ddof": ddof},
    )


def stressed_fx_net(net_amount, eur_per_unit, shock):
    """Adverse EUR value after currency-level asset/liability netting."""
    net = number(net_amount, "net_amount")
    fx = number(eur_per_unit, "eur_per_unit", 0, strict_min=True)
    shock = number(shock, "shock", 0)
    if net > 0 and shock > 1:
        raise PfandbriefError(
            "INVALID_STRESS", "positive net asset implies negative stressed FX rate"
        )
    base = net * fx
    loss = abs(net) * fx * shock
    return CalcResult(
        base - loss,
        "stressed_fx_net",
        ("PfandBarwertV §6",),
        "EUR",
        details={"base_eur": base, "stress_loss": loss},
    )
