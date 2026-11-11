"""Dated evidence, profiles and conservation controls. AGPL-3.0-only."""

from copy import deepcopy
from .core import (
    CalcResult,
    PfandbriefError,
    choice,
    flag,
    input_fingerprint,
    iso_date,
    number,
)


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise PfandbriefError("INVALID_TEXT", f"{name} must be nonempty text")
    return value


def _records(rows, required, name):
    if not isinstance(rows, (list, tuple)):
        raise PfandbriefError("INVALID_TABLE", f"{name} must be a list of records")
    for row in rows:
        if not isinstance(row, dict) or not set(required) <= row.keys():
            raise PfandbriefError(
                "MISSING_FIELD", f"{name} row needs {tuple(required)}"
            )
    return rows


def _unique(rows, fields):
    seen = set()
    for row in rows:
        key = tuple(_text(row[f], f) for f in fields)
        if key in seen:
            raise PfandbriefError("DUPLICATE_KEY", f"duplicate {fields}: {key}")
        seen.add(key)


def _dated(row):
    start, end, known = [
        iso_date(row[k], k) for k in ("valid_from", "valid_to", "known_from")
    ]
    if end < start:
        raise PfandbriefError("DATE_ORDER", "valid_to precedes valid_from")
    return start, end, known


def _latest(rows, key, known_at):
    selected = {}
    for row in rows:
        stamp = iso_date(row["known_from"], "known_from")
        if stamp > known_at:
            continue
        identity = row[key]
        if identity not in selected or stamp > iso_date(
            selected[identity]["known_from"], "known_from"
        ):
            selected[identity] = row
        elif stamp == iso_date(selected[identity]["known_from"], "known_from"):
            raise PfandbriefError(
                "AMBIGUOUS_REVISION", "multiple revisions at the same knowledge date"
            )
    return list(selected.values())


def select_rule_profile(
    profiles, profile_id, as_of, known_at, *, allow_experimental=False
):
    """Choose latest known revision before checking validity; never resurrect withdrawn dates."""
    fields = (
        "profile_id",
        "revision",
        "valid_from",
        "valid_to",
        "known_from",
        "status",
        "source_ref",
        "parameters",
    )
    rows = _records(profiles, fields, "profiles")
    _unique(rows, ("profile_id", "revision"))
    requested = _text(profile_id, "profile_id")
    day, known = iso_date(as_of, "as_of"), iso_date(known_at, "known_at")
    flag(allow_experimental, "allow_experimental")
    for row in rows:
        _dated(row)
        choice(row["status"], "status", ("VERIFIED", "EXPERIMENTAL"))
        _text(row["source_ref"], "source_ref")
        if not isinstance(row["parameters"], dict):
            raise PfandbriefError("INVALID_TABLE", "parameters must be a mapping")
        input_fingerprint(row["parameters"])
    candidates = _latest(
        [r for r in rows if r["profile_id"] == requested], "profile_id", known
    )
    if not candidates:
        raise PfandbriefError(
            "UNKNOWN_PROFILE", "no known revision for requested profile"
        )
    row = candidates[0]
    start, end, _ = _dated(row)
    if not start <= day <= end:
        raise PfandbriefError("PROFILE_DATE", "selected revision is not valid at as_of")
    if row["status"] != "VERIFIED" and not allow_experimental:
        raise PfandbriefError(
            "UNVERIFIED_PROFILE", "experimental profile requires explicit opt-in"
        )
    return CalcResult(
        deepcopy(row["parameters"]),
        "select_rule_profile",
        (row["source_ref"],),
        "parameters",
        details={
            "profile_id": requested,
            "revision": row["revision"],
            "profile_status": row["status"],
            "as_of": day.isoformat(),
            "known_at": known.isoformat(),
        },
        limitations=(
            "Profile status is supplied provenance, not authentication of a legal review",
        ),
    )


def assess_evidence(requirements, evidence, as_of, known_at):
    """Check supplied dated evidence; preserve missing, expired, future and failed states."""
    reqs = _records(
        requirements,
        ("requirement_id", "scope", "allow_not_applicable", "source_ref"),
        "requirements",
    )
    _unique(reqs, ("requirement_id", "scope"))
    if not reqs:
        raise PfandbriefError(
            "EMPTY_REQUIREMENTS", "provide an explicit nonempty requirement set"
        )
    fields = (
        "evidence_id",
        "requirement_id",
        "scope",
        "valid_from",
        "valid_to",
        "known_from",
        "conclusion",
        "reviewer",
        "source_ref",
        "reason",
    )
    rows = _records(evidence, fields, "evidence")
    _unique(rows, ("evidence_id", "known_from"))
    day, known = iso_date(as_of, "as_of"), iso_date(known_at, "known_at")
    reqkeys = {(r["requirement_id"], r["scope"]) for r in reqs}
    identities = {}
    for row in rows:
        _dated(row)
        for k in ("requirement_id", "scope", "reviewer", "source_ref", "reason"):
            _text(row[k], k)
        choice(row["conclusion"], "conclusion", ("MET", "NOT_MET", "NOT_APPLICABLE"))
        pair = (row["requirement_id"], row["scope"])
        if pair not in reqkeys:
            raise PfandbriefError(
                "UNKNOWN_REQUIREMENT",
                "evidence targets an unspecified requirement/scope",
            )
        if row["evidence_id"] in identities and identities[row["evidence_id"]] != pair:
            raise PfandbriefError(
                "IDENTITY_CHANGE",
                "evidence identity cannot change requirement or scope",
            )
        identities[row["evidence_id"]] = pair
    latest = _latest(rows, "evidence_id", known)
    checks = []
    for req in reqs:
        allow = flag(req["allow_not_applicable"], "allow_not_applicable")
        _text(req["source_ref"], "source_ref")
        relevant = [
            r
            for r in latest
            if (r["requirement_id"], r["scope"])
            == (req["requirement_id"], req["scope"])
        ]
        active = [r for r in relevant if _dated(r)[0] <= day <= _dated(r)[1]]
        conclusions = {r["conclusion"] for r in active}
        if len(conclusions) > 1:
            raise PfandbriefError(
                "CONFLICTING_EVIDENCE", "active evidence has conflicting conclusions"
            )
        if active:
            status = active[0]["conclusion"]
            if status == "NOT_APPLICABLE" and not allow:
                status = "INVALID_NOT_APPLICABLE"
        elif any(_dated(r)[1] < day for r in relevant):
            status = "EXPIRED"
        elif relevant:
            status = "FUTURE"
        else:
            status = "MISSING"
        checks.append(
            {
                "requirement_id": req["requirement_id"],
                "scope": req["scope"],
                "status": status,
                "evidence_ids": sorted(r["evidence_id"] for r in active),
                "source_ref": req["source_ref"],
            }
        )
    states = {r["status"] for r in checks}
    decision = (
        "FAILED"
        if states & {"NOT_MET", "INVALID_NOT_APPLICABLE"}
        else (
            "INCOMPLETE"
            if states & {"MISSING", "EXPIRED", "FUTURE"}
            else "CHECKS_PASSED"
        )
    )
    return CalcResult(
        decision,
        "assess_evidence",
        unit="decision",
        details={
            "checks": checks,
            "as_of": day.isoformat(),
            "known_at": known.isoformat(),
        },
        limitations=(
            "Checks presence, timing and consistency; does not authenticate evidence or prove all legal duties were included",
        ),
    )


def validate_allocations(claims, collateral, allocations):
    """Conserve explicit claim and qualified collateral capacities; no rank optimization."""
    claims = _records(claims, ("claim_id", "capacity", "currency", "kind"), "claims")
    collateral = _records(
        collateral, ("collateral_id", "capacity", "currency", "kind"), "collateral"
    )
    alloc = _records(
        allocations,
        ("allocation_id", "claim_id", "collateral_id", "kind", "currency", "amount"),
        "allocations",
    )
    _unique(claims, ("claim_id",))
    _unique(collateral, ("collateral_id",))
    _unique(alloc, ("allocation_id",))
    tables = []
    for rows, key in ((claims, "claim_id"), (collateral, "collateral_id")):
        table = {}
        for r in rows:
            cap = number(r["capacity"], "capacity", 0)
            _text(r["currency"], "currency")
            choice(r["kind"], "kind", ("HYP", "OEF", "SCH", "FLG"))
            table[r[key]] = {
                "capacity": cap,
                "currency": r["currency"],
                "kind": r["kind"],
                "allocated": 0.0,
            }
        tables.append(table)
    claimmap, colmap = tables
    for r in alloc:
        _text(r["claim_id"], "claim_id")
        _text(r["collateral_id"], "collateral_id")
        if r["claim_id"] not in claimmap or r["collateral_id"] not in colmap:
            raise PfandbriefError(
                "UNKNOWN_KEY", "allocation references an unknown claim or collateral"
            )
        c, k = claimmap[r["claim_id"]], colmap[r["collateral_id"]]
        if not r["currency"] == c["currency"] == k["currency"]:
            raise PfandbriefError("CURRENCY_MISMATCH", "allocation currency differs")
        if not r["kind"] == c["kind"] == k["kind"]:
            raise PfandbriefError(
                "KIND_MISMATCH", "allocation crosses Pfandbrief kinds"
            )
        amount = number(r["amount"], "amount", 0)
        c["allocated"] += amount
        k["allocated"] += amount
    for table in tables:
        for r in table.values():
            if r["allocated"] > r["capacity"]:
                raise PfandbriefError(
                    "OVERALLOCATION", "claim or collateral capacity exceeded"
                )
            r["remaining"] = r["capacity"] - r["allocated"]
    return CalcResult(
        True,
        "validate_allocations",
        ("PfandBG §§5(1a),18(2),22(4); explicit qualified capacities",),
        "boolean",
        details={
            "claims": claimmap,
            "collateral": colmap,
            "allocation_count": len(alloc),
        },
        limitations=(
            "Legal rank and qualified capacities are separately established inputs",
        ),
    )


def register_snapshot(events, as_of, known_at):
    """Replay local evidenced events; never edits input history or a live legal register."""
    fields = (
        "event_id",
        "asset_id",
        "kind",
        "effective_date",
        "recorded_at",
        "sequence",
        "action",
        "payload",
        "reason",
        "evidence_ref",
    )
    rows = _records(events, fields, "events")
    _unique(rows, ("event_id",))
    day, known = iso_date(as_of, "as_of"), iso_date(known_at, "known_at")
    relevant = []
    keys = set()
    for r in rows:
        for k in ("asset_id", "reason", "evidence_ref"):
            _text(r[k], k)
        choice(r["kind"], "kind", ("HYP", "OEF", "SCH", "FLG"))
        choice(r["action"], "action", ("ADD", "UPDATE", "REMOVE"))
        effective, recorded = (
            iso_date(r["effective_date"], "effective_date"),
            iso_date(r["recorded_at"], "recorded_at"),
        )
        seq = number(r["sequence"], "sequence", 0)
        if seq != int(seq):
            raise PfandbriefError("OUT_OF_RANGE", "event sequence must be whole")
        if not isinstance(r["payload"], dict):
            raise PfandbriefError("INVALID_TABLE", "event payload must be a mapping")
        input_fingerprint(r["payload"])
        if r["action"] == "REMOVE" and r["payload"]:
            raise PfandbriefError("NOT_APPLICABLE", "REMOVE requires empty payload")
        if effective <= day and recorded <= known:
            key = (r["asset_id"], effective, seq)
            if key in keys:
                raise PfandbriefError(
                    "AMBIGUOUS_EVENT", "duplicate effective event sequence"
                )
            keys.add(key)
            relevant.append(r)
    relevant.sort(key=lambda r: (r["effective_date"], r["sequence"], r["event_id"]))
    active = {}
    applied = []
    kinds = {}
    for r in relevant:
        ident = r["asset_id"]
        if ident in kinds and kinds[ident] != r["kind"]:
            raise PfandbriefError("KIND_MISMATCH", "asset kind cannot change")
        kinds[ident] = r["kind"]
        if r["action"] == "ADD":
            if ident in active:
                raise PfandbriefError(
                    "DUPLICATE_ASSET", "ADD cannot overwrite active asset"
                )
            active[ident] = {
                "asset_id": ident,
                "kind": r["kind"],
                "payload": deepcopy(r["payload"]),
            }
        else:
            if ident not in active:
                raise PfandbriefError(
                    "UNKNOWN_ASSET", "UPDATE/REMOVE requires active asset"
                )
            if r["action"] == "REMOVE":
                del active[ident]
            else:
                active[ident]["payload"] = deepcopy(r["payload"])
        applied.append(r["event_id"])
    return CalcResult(
        [active[k] for k in sorted(active)],
        "register_snapshot",
        ("PfandBG §5; local event model",),
        "records",
        details={
            "applied_events": applied,
            "as_of": day.isoformat(),
            "known_at": known.isoformat(),
        },
        limitations=(
            "Technical reconstruction does not establish trustee approval or legal registration",
        ),
    )
