"""Local register-entry checks and explicit maturity-extension scenarios.

Copyright 2026 RiskDataScience GmbH. SPDX-License-Identifier: AGPL-3.0-only
"""

from .core import CalcResult, PfandbriefError, choice, number, iso_date
from .controls import _records, _unique, _text
from .pools import _kind
from .finance import _month_date, year_fraction
from .eu import _proof


def validate_register_entries(entries, used_numbers):
    """Check proposed admissions and fields; never writes a legal cover register."""
    fields = (
        "entry_id",
        "kind",
        "register_id",
        "number",
        "entry_date",
        "recorded_date",
        "category",
        "fields",
        "features",
    )
    rows = _records(entries, fields, "entries")
    _unique(rows, ("entry_id",))
    history = _records(used_numbers, ("kind", "register_id", "number"), "used_numbers")
    used = set()
    maximum = {}

    def key(row):
        kind = choice(row["kind"], "kind", ("HYP", "OEF", "SCH", "FLG"))
        reg = _text(row["register_id"], "register_id")
        n = number(row["number"], "number", 1)
        if n != int(n):
            raise PfandbriefError(
                "INVALID_NUMBER", "register number must be a positive integer"
            )
        return kind, reg, int(n)

    for r in history:
        k = key(r)
        if k in used:
            raise PfandbriefError(
                "DUPLICATE_KEY", "historical register number occurs twice"
            )
        used.add(k)
        maximum[k[:2]] = max(maximum.get(k[:2], 0), k[2])
    common = ["file_ref"]
    security = [
        "object_ref",
        "lending_value",
        "lien_ref",
        "lien_currency",
        "lien_nominal",
    ]
    public = ["debtor", "claim_ref", "currency", "nominal"]
    derivative = [
        "counterparty_name",
        "counterparty_address",
        "product_terms",
        "counterparty_ref",
        "framework_date",
        "trade_date",
        "original_tenor",
        "maturity",
        "collateral_details",
        "trustee_consent_ref",
    ]
    extras = {
        "non_accessory": [
            "claim_debtor",
            "claim_currency",
            "claim_nominal",
            "loan_ref",
        ],
        "guaranteed": ["guarantor"],
        "partial": ["assigned_part", "relative_rank"],
        "refinancing": [
            "refinancing_institution",
            "refinancing_timestamp",
            "refinancing_legal_basis",
        ],
        "fiduciary": ["transfer_creditor"],
        "insurance_assignment": ["insurance_security_ref"],
        "deposit": ["account_bank", "iban"],
        "indemnity": ["indemnifier_name", "indemnifier_address"],
        "sovereign_security": ["debt_form"],
    }
    checked = []
    # Input order is the proposed legal admission order, not an event-history sort.
    for r in rows:
        k = key(r)
        day = iso_date(r["entry_date"], "entry_date")
        recorded = iso_date(r["recorded_date"], "recorded_date")
        category = choice(
            r["category"],
            "category",
            ("MORTGAGE", "PUBLIC", "SHIP", "AIRCRAFT", "SUBSTITUTE", "DERIVATIVE"),
        )
        expected = {
            "MORTGAGE": "HYP",
            "PUBLIC": "OEF",
            "SHIP": "SCH",
            "AIRCRAFT": "FLG",
        }
        if category in expected and expected[category] != k[0]:
            raise PfandbriefError(
                "KIND_MISMATCH", "primary register category differs from kind"
            )
        data = r["fields"]
        if not isinstance(data, dict):
            raise PfandbriefError("INVALID_TABLE", "fields must be a mapping")
        features = r["features"]
        if not isinstance(features, (list, tuple)) or any(
            f not in extras for f in features
        ):
            raise PfandbriefError("INVALID_FEATURE", "unknown register field feature")
        if len(set(features)) != len(features):
            raise PfandbriefError("DUPLICATE_KEY", "duplicate register feature")
        required = common + (
            security
            if category in ("MORTGAGE", "SHIP", "AIRCRAFT")
            else derivative
            if category == "DERIVATIVE"
            else public
        )
        for feature in features:
            required += extras[feature]
        if day < iso_date("2023-07-01", "boundary"):
            legacy = r.get("legacy_fields")
            if (
                not isinstance(legacy, (list, tuple))
                or not legacy
                or any(not isinstance(f, str) or not f for f in legacy)
            ):
                raise PfandbriefError(
                    "MISSING_LEGACY_SCHEMA",
                    "historical entry requires explicit legacy_fields and source",
                )
            _text(r.get("legacy_source_ref"), "legacy_source_ref")
            required = list(legacy)
        missing = [
            name
            for name in required
            if name not in data or data[name] is None or data[name] == ""
        ]
        for name in ("lending_value", "lien_nominal", "nominal", "claim_nominal"):
            if name in data and name not in missing:
                number(data[name], name, 0)
        checks = {
            "entry_date_matches_recording": day == recorded,
            "number_unused": k not in used,
            "number_increases": k[2] > maximum.get(k[:2], 0),
        }
        state = (
            "FAILED"
            if not all(checks.values())
            else "INCOMPLETE"
            if missing
            else "CHECKS_PASSED"
        )
        checked.append(
            {
                "entry_id": r["entry_id"],
                "decision": state,
                "checks": checks,
                "required_fields": list(dict.fromkeys(required)),
                "missing_fields": missing,
            }
        )
        used.add(k)
        maximum[k[:2]] = max(maximum.get(k[:2], 0), k[2])
    decision = (
        "FAILED"
        if any(r["decision"] == "FAILED" for r in checked)
        else "INCOMPLETE"
        if any(r["decision"] == "INCOMPLETE" for r in checked)
        else "CHECKS_PASSED"
    )
    return CalcResult(
        decision,
        "validate_register_entries",
        ("DeckRegV §§8–14,18",),
        "decision",
        details={"entries": checked},
        limitations=(
            "Input features must fully describe applicable rights and arrangements; legal contents are not authenticated",
            "used_numbers must include previously deleted entries; this is a proposed-admission check, not a historical correction model",
        ),
    )


def deferred_interest(amount, coupon_rate, original_date, new_date, day_count):
    """Simple contractual accrual on a deferred amount, including capitalized overdue interest."""
    principal = number(amount, "amount", 0)
    rate = number(coupon_rate, "coupon_rate")
    years = year_fraction(original_date, new_date, day_count).value
    if rate * years < -1:
        raise PfandbriefError(
            "INVALID_RATE", "negative accrual exceeds deferred amount"
        )
    interest = principal * rate * years
    return CalcResult(
        interest,
        "deferred_interest",
        ("PfandBG §30(2a) sentence8–9; explicit contractual accrual",),
        "currency",
        details={
            "deferred_amount": principal,
            "year_fraction": years,
            "repayment_with_interest": principal + interest,
        },
        limitations=(
            "Applies the supplied existing coupon and convention; differing contractual agreements require explicit inputs",
        ),
    )


def interest_extension(
    amount,
    coupon_rate,
    original_date,
    appointment_date,
    decision_date,
    day_count,
    *,
    authority_status,
):
    """First-month interest deferral to the end of the month following appointment."""
    original, appointment, decided = (
        iso_date(original_date, "original_date"),
        iso_date(appointment_date, "appointment_date"),
        iso_date(decision_date, "decision_date"),
    )
    end = _month_date(appointment, 1, False)
    proof = _proof(authority_status, "authority_status")
    if not appointment <= decided <= original <= end:
        raise PfandbriefError(
            "INVALID_EXTENSION_DATE",
            "interest must fall within the first month and follow the decision",
        )
    result = deferred_interest(amount, coupon_rate, original, end, day_count)
    decision = (
        "CHECKS_PASSED"
        if proof == "MET"
        else "FAILED"
        if proof == "NOT_MET"
        else "INCOMPLETE"
    )
    return CalcResult(
        {
            "date": end.isoformat(),
            "deferred_interest_payment": number(amount, "amount", 0),
            "additional_interest": result.value,
        },
        "interest_extension",
        ("PfandBG §30(2a) sentence4,(2b)",),
        "payment",
        details={
            "decision": decision,
            "original_date": original.isoformat(),
            "year_fraction": result.details["year_fraction"],
        },
        limitations=(
            "Requires evidenced administrator authority and separate reconciliation of all affected emissions",
        ),
    )


def extension_plan(
    kind,
    issues,
    appointment_date,
    decision_date,
    *,
    authority_status,
    conditions_status,
    complete_scope_status,
):
    """Check an issue-uniform principal deferral scenario and repayment order."""
    fields = (
        "issue_id",
        "kind",
        "original_date",
        "new_date",
        "principal",
        "shifted_fraction",
        "coupon_rate",
        "day_count",
    )
    rows = _records(issues, fields, "issues")
    _unique(rows, ("issue_id",))
    _kind(rows, kind)
    if not rows:
        raise PfandbriefError("EMPTY_PLAN", "supply at least one bond issue")
    appointment = iso_date(appointment_date, "appointment_date")
    decided = iso_date(decision_date, "decision_date")
    if decided < appointment:
        raise PfandbriefError("DATE_ORDER", "decision precedes appointment")
    authority = _proof(authority_status, "authority_status")
    conditions = _proof(conditions_status, "conditions_status")
    complete = _proof(complete_scope_status, "complete_scope_status")
    month_end = _month_date(appointment, 1, False)
    prepared = []
    payments = []
    checks = []
    needs_conditions = False
    for r in rows:
        original = iso_date(r["original_date"], "original_date")
        new = iso_date(r["new_date"], "new_date")
        if new < original:
            raise PfandbriefError("DATE_ORDER", "extended date precedes original date")
        n = number(r["principal"], "principal", 0, strict_min=True)
        f = number(r["shifted_fraction"], "shifted_fraction", 0, 1)
        number(r["coupon_rate"], "coupon_rate")
        changed = f > 0 and new > original
        if (f == 0 and new != original) or (f > 0 and new == original):
            raise PfandbriefError(
                "INCONSISTENT_EXTENSION",
                "zero shift has unchanged date; positive shift needs a later date",
            )
        checks.append(
            {
                "check": "maximum_extension:" + r["issue_id"],
                "passed": new <= _month_date(original, 12, False),
            }
        )
        checks.append(
            {
                "check": "decision_before_due:" + r["issue_id"],
                "passed": not changed or decided <= original,
            }
        )
        if changed and new > month_end:
            needs_conditions = True
        accrual = deferred_interest(
            n * f, r["coupon_rate"], original, new, r["day_count"]
        )
        if f < 1:
            payments.append(
                {
                    "issue_id": r["issue_id"],
                    "date": original.isoformat(),
                    "principal": n * (1 - f),
                    "additional_interest": 0.0,
                }
            )
        if f > 0:
            payments.append(
                {
                    "issue_id": r["issue_id"],
                    "date": new.isoformat(),
                    "principal": n * f,
                    "additional_interest": accrual.value,
                }
            )
        prepared.append(
            {"issue_id": r["issue_id"], "original": original, "new": new, "fraction": f}
        )
    dates = sorted({iso_date(p["date"], "date") for p in payments})
    for day in dates:
        for earlier in prepared:
            paid_early = (
                1 - earlier["fraction"] if day >= earlier["original"] else 0.0
            ) + (earlier["fraction"] if day >= earlier["new"] else 0.0)
            if paid_early >= 1:
                continue
            for later in prepared:
                if not earlier["original"] < later["original"] <= day:
                    continue
                paid_late = (
                    1 - later["fraction"] if day >= later["original"] else 0.0
                ) + (later["fraction"] if day >= later["new"] else 0.0)
                checks.append(
                    {
                        "check": "repayment_order:"
                        + earlier["issue_id"]
                        + ":"
                        + later["issue_id"]
                        + ":"
                        + day.isoformat(),
                        "passed": paid_late <= paid_early,
                    }
                )
    statuses = [authority, complete] + ([conditions] if needs_conditions else [])
    decision = (
        "FAILED"
        if "NOT_MET" in statuses or not all(r["passed"] for r in checks)
        else "INCOMPLETE"
        if "MISSING" in statuses
        else "CHECKS_PASSED"
    )
    payments.sort(key=lambda r: (r["date"], r["issue_id"]))
    return CalcResult(
        decision,
        "extension_plan",
        ("PfandBG §30(2a),(2b),(7)",),
        "decision",
        details={
            "kind": kind,
            "payments": payments,
            "checks": checks,
            "conditions_presumed": not needs_conditions,
            "first_month_end": month_end.isoformat(),
        },
        limitations=(
            "Explicit principal-only two-payment scenario per issue; no automatic modification of base cashflows",
            "Complete scope evidence must cover all affected issues, interest-payment interactions and contractual departures",
            "Derivatives and new administrator liabilities are outside the statutory deferral power",
        ),
    )
