"""Numeric metrics and explicit local CSV exports, not supervisory reporting.

Copyright 2026 RiskDataScience GmbH. SPDX-License-Identifier: AGPL-3.0-only
"""

import csv
from pathlib import Path
from .core import CalcResult, PfandbriefError, number, flag, iso_date
from .controls import _records, _unique, _text
from .finance import _month_date


def pool_metrics(result):
    """Extract reconciled metrics from one analyze_pool result, retaining its decision."""
    if not isinstance(result, CalcResult) or result.method != "analyze_pool":
        raise PfandbriefError(
            "INVALID_RESULT", "pool_metrics requires an analyze_pool result"
        )
    d = result.details
    cover = d["coverage"]["details"]
    liquid = d["liquidity"]
    values = {
        k: cover[k]
        for k in (
            "assets_nominal",
            "liabilities_nominal",
            "assets_pv",
            "liabilities_pv",
            "allocated_nominal_oc",
            "allocated_pv_oc",
            "nominal_headroom",
            "pv_headroom",
        )
    }
    values["nominal_surplus"] = cover["assets_nominal"] - cover["liabilities_nominal"]
    values["pv_surplus"] = cover["assets_pv"] - cover["liabilities_pv"]
    for view in ("nominal", "pv"):
        den = cover["liabilities_" + view]
        values[view + "_oc_ratio"] = (
            None if den == 0 else values[view + "_surplus"] / den
        )
    values.update(
        liquidity_required=liquid["value"],
        liquidity_buffer=liquid["details"]["buffer"],
        liquidity_headroom=liquid["details"]["headroom"],
        stress_deficit=d["stress"]["value"],
        worst_stress_balance=d["stress"]["details"]["worst_balance"],
    )
    balances = liquid["details"]["cumulative"]
    values["liquidity_peak_day"] = (
        None if liquid["value"] == 0 else balances.index(min(balances)) + 1
    )
    rows = [
        {
            "kind": d["kind"],
            "as_of": d["as_of"],
            "metric": k,
            "value": v,
            "unit": "fraction"
            if k.endswith("_ratio")
            else "day_index"
            if k == "liquidity_peak_day"
            else "EUR",
            "decision": result.value,
            "hypothetical": d["hypothetical"],
        }
        for k, v in values.items()
    ]
    return CalcResult(
        rows,
        "pool_metrics",
        ("PfandBG §28(1) numeric subset; underlying calculation results",),
        "records",
        details={
            "kind": d["kind"],
            "decision": result.value,
            "source_method": result.method,
        },
        limitations=(
            "No complete statutory disclosure or supervisory filing; stress is reported as a net balance",
        ),
    )


def aggregate_positions(positions, group_fields, value_field):
    """Explicit amount aggregation over unique positions; grouping fields must be strings."""
    if not isinstance(group_fields, (list, tuple)) or not group_fields:
        raise PfandbriefError(
            "INVALID_GROUP", "provide a nonempty list of grouping fields"
        )
    for k in group_fields:
        _text(k, "group_field")
    if len(set(group_fields)) != len(group_fields):
        raise PfandbriefError("DUPLICATE_KEY", "duplicate grouping field")
    value_field = _text(value_field, "value_field")
    if value_field in group_fields:
        raise PfandbriefError("INVALID_GROUP", "value field cannot also group")
    rows = _records(positions, ("position_id", value_field, *group_fields), "positions")
    _unique(rows, ("position_id",))
    groups = {}
    for r in rows:
        key = tuple(_text(r[k], k) for k in group_fields)
        groups[key] = groups.get(key, 0.0) + number(r[value_field], value_field)
    output = [
        {**dict(zip(group_fields, key)), value_field: groups[key]}
        for key in sorted(groups)
    ]
    return CalcResult(
        output,
        "aggregate_positions",
        unit="records",
        details={
            "group_fields": list(group_fields),
            "value_field": value_field,
            "position_count": len(rows),
            "total": sum(groups.values()),
        },
        limitations=(
            "Caller must group by kind and currency wherever amounts are not homogeneous",
        ),
    )


def maturity_buckets(positions, as_of):
    """Calendar-month bands for explicitly supplied maturity or repricing dates."""
    rows = _records(
        positions, ("position_id", "kind", "currency", "amount", "date"), "positions"
    )
    _unique(rows, ("position_id",))
    day = iso_date(as_of, "as_of")
    scopes = {(r["kind"], r["currency"]) for r in rows}
    if len(scopes) > 1:
        raise PfandbriefError(
            "SCOPE_MISMATCH", "maturity bands require one kind and currency"
        )
    thresholds = (6, 12, 18, 24, 36, 48, 60, 120)
    labels = (
        "LE6M",
        "GT6LE12M",
        "GT12LE18M",
        "GT18LE24M",
        "GT24LE36M",
        "GT36LE48M",
        "GT48LE60M",
        "GT60LE120M",
        "GT120M",
    )
    boundaries = [_month_date(day, n, False) for n in thresholds]
    totals = dict.fromkeys(labels, 0.0)
    assigned = []
    overdue = 0.0
    for r in rows:
        _text(r["kind"], "kind")
        _text(r["currency"], "currency")
        amount = number(r["amount"], "amount", 0)
        due = iso_date(r["date"], "date")
        index = next((i for i, boundary in enumerate(boundaries) if due <= boundary), 8)
        band = labels[index]
        totals[band] += amount
        if due < day:
            overdue += amount
        assigned.append(
            {"position_id": r["position_id"], "bucket": band, "amount": amount}
        )
    return CalcResult(
        [{"bucket": k, "amount": v} for k, v in totals.items()],
        "maturity_buckets",
        ("PfandBG §28(1)4",),
        "records",
        details={
            "as_of": day.isoformat(),
            "boundaries": [x.isoformat() for x in boundaries],
            "overdue_amount": overdue,
            "positions": assigned,
        },
        limitations=(
            "Use bond maturity for liabilities and contractual repricing date for cover assets",
        ),
    )


def weighted_ltv(positions):
    """§28(2)3 LTV: used lien plus prior/equal liens; highest used lien per property."""
    rows = _records(
        positions,
        (
            "position_id",
            "property_id",
            "allocated_amount",
            "used_lien_with_prior_equal",
            "lending_value",
        ),
        "positions",
    )
    _unique(rows, ("position_id",))
    numerator = denominator = 0.0
    details = []
    groups = {}
    for r in rows:
        prop = _text(r["property_id"], "property_id")
        weight = number(r["allocated_amount"], "allocated_amount", 0)
        loan = number(r["used_lien_with_prior_equal"], "used_lien_with_prior_equal", 0)
        value = number(r["lending_value"], "lending_value", 0, strict_min=True)
        ratio = loan / value
        item = {
            "position_id": r["position_id"],
            "property_id": prop,
            "weight": weight,
            "ltv": ratio,
            "weighted_contribution": weight * ratio,
        }
        details.append(item)
        if weight > 0:
            groups.setdefault(prop, []).append(item)
    selected = []
    for prop in sorted(groups):
        highest = max(x["ltv"] for x in groups[prop])
        candidates = [x for x in groups[prop] if x["ltv"] == highest]
        if len(candidates) > 1:
            raise PfandbriefError(
                "AMBIGUOUS_COLLATERAL",
                "equal highest liens require explicit consolidation before weighting",
            )
        item = candidates[0]
        selected.append(item["position_id"])
        numerator += item["weighted_contribution"]
        denominator += item["weight"]
    return CalcResult(
        None if denominator == 0 else numerator / denominator,
        "weighted_ltv",
        ("PfandBG §28(2)3",),
        "fraction",
        details={
            "total_weight": denominator,
            "weighted_sum": numerator,
            "positions": details,
            "selected_position_ids": selected,
            "ignored_position_ids": sorted(
                r["position_id"] for r in rows if r["position_id"] not in selected
            ),
        },
        limitations=(
            "Uses the cover-used lien, not the full borrower loan; prior and equal third-party liens must already be included",
            "Same-property liens retain only the highest LTV and that claim's weight; equal maxima require consolidation",
        ),
    )


def reconcile_totals(
    actual, expected, *, absolute_tolerance=1e-8, relative_tolerance=1e-12
):
    """Numerical reconciliation tolerance; never changes a statutory limit decision."""
    if not isinstance(actual, dict) or not isinstance(expected, dict):
        raise PfandbriefError("INVALID_TABLE", "totals must be mappings")
    atol = number(absolute_tolerance, "absolute_tolerance", 0)
    rtol = number(relative_tolerance, "relative_tolerance", 0)
    checks = []
    for key in set(actual) | set(expected):
        _text(key, "metric")
    for key in sorted(set(actual) | set(expected)):
        _text(key, "metric")
        if (
            key not in actual
            or key not in expected
            or actual[key] is None
            or expected[key] is None
        ):
            checks.append(
                {
                    "metric": key,
                    "decision": "INCOMPLETE",
                    "difference": None,
                    "tolerance": None,
                }
            )
        else:
            a, e = number(actual[key], "actual"), number(expected[key], "expected")
            difference, tolerance = a - e, atol + rtol * abs(e)
            checks.append(
                {
                    "metric": key,
                    "decision": "CHECKS_PASSED"
                    if abs(difference) <= tolerance
                    else "FAILED",
                    "difference": difference,
                    "tolerance": tolerance,
                }
            )
    states = {r["decision"] for r in checks}
    return CalcResult(
        "FAILED"
        if "FAILED" in states
        else "INCOMPLETE"
        if "INCOMPLETE" in states
        else "CHECKS_PASSED",
        "reconcile_totals",
        unit="decision",
        details={"checks": checks},
    )


def export_table(rows, path, *, overwrite=False):
    """Write flat scalar records to an explicit CSV path; no package-resource writes."""
    flag(overwrite, "overwrite")
    rows = _records(rows, (), "rows")
    if not rows:
        raise PfandbriefError(
            "EMPTY_TABLE", "CSV export needs column names from a nonempty table"
        )
    columns = list(rows[0])
    if not columns:
        raise PfandbriefError("EMPTY_TABLE", "CSV export needs at least one column")
    for name in columns:
        _text(name, "column")
    formatted = []
    for row in rows:
        if set(row) != set(columns):
            raise PfandbriefError(
                "COLUMN_MISMATCH", "all records need identical columns"
            )
        output = []
        for k in columns:
            v = row[k]
            if v is None:
                output.append("")
            elif isinstance(v, bool):
                output.append("true" if v else "false")
            elif isinstance(v, str):
                output.append(v)
            else:
                output.append(format(number(v, k), ".17g"))
        formatted.append(output)
    try:
        target = Path(path).resolve()
    except (TypeError, ValueError) as exc:
        raise PfandbriefError("INVALID_PATH", "path must be a local filename") from exc
    if target.is_relative_to(Path(__file__).resolve().parent):
        raise PfandbriefError(
            "READ_ONLY_RESOURCE", "cannot export into installed package resources"
        )
    try:
        with target.open(
            "w" if overwrite else "x", encoding="utf-8", newline=""
        ) as stream:
            writer = csv.writer(stream, quoting=csv.QUOTE_ALL, lineterminator="\n")
            writer.writerow(columns)
            writer.writerows(formatted)
    except FileExistsError as exc:
        raise PfandbriefError("TARGET_EXISTS", "explicit overwrite required") from exc
    except OSError as exc:
        raise PfandbriefError("EXPORT_ERROR", str(exc)) from exc
    return CalcResult(
        str(target),
        "export_table",
        unit="file",
        details={"rows": len(rows), "columns": columns, "format": "CSV_UTF8"},
    )
