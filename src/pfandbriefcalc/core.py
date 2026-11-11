"""Shared result and validation contracts. Copyright 2026 RiskDataScience GmbH.

SPDX-License-Identifier: AGPL-3.0-only
"""

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from hashlib import sha256
import json
import math
from numbers import Real
from typing import Any


class PfandbriefError(ValueError):
    """Controlled input/method error with a stable machine-readable code."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class CalcResult:
    """Calculated output; calculation success does not imply regulatory approval."""

    value: Any
    method: str
    sources: tuple[str, ...] = ()
    unit: str = "unspecified"
    status: str = "CALCULATED"
    details: dict[str, Any] = field(default_factory=dict)
    limitations: tuple[str, ...] = ()

    def __post_init__(self):
        def check(obj):
            if isinstance(obj, Real) and not math.isfinite(obj):
                raise PfandbriefError("NUMERIC_RANGE", "nonfinite calculation result")
            if isinstance(obj, dict):
                for value in obj.values():
                    check(value)
            elif isinstance(obj, (list, tuple)):
                for value in obj:
                    check(value)

        check(self.value)
        check(self.details)

    def as_dict(self) -> dict:
        return asdict(self)


def number(value, name, minimum=None, maximum=None, strict_min=False):
    try:
        valid = (
            not isinstance(value, bool)
            and isinstance(value, Real)
            and math.isfinite(value)
        )
    except (OverflowError, ValueError):
        valid = False
    if not valid:
        raise PfandbriefError("INVALID_NUMBER", f"{name} must be a finite real scalar")
    x = float(value)
    if minimum is not None and (x < minimum or (strict_min and x == minimum)):
        raise PfandbriefError("OUT_OF_RANGE", f"{name} below its allowed boundary")
    if maximum is not None and x > maximum:
        raise PfandbriefError("OUT_OF_RANGE", f"{name} above its allowed boundary")
    return x


def choice(value, name, options):
    if not isinstance(value, str) or value not in options:
        raise PfandbriefError(
            "INVALID_CHOICE", f"{name} must be one of {tuple(options)}"
        )
    return value


def vector(values, name, minimum=None):
    if isinstance(values, (str, bytes, dict)):
        raise PfandbriefError("INVALID_VECTOR", f"{name} must be a numeric sequence")
    try:
        return [number(v, name, minimum) for v in values]
    except TypeError as exc:
        raise PfandbriefError(
            "INVALID_VECTOR", f"{name} must be a numeric sequence"
        ) from exc


def flag(value, name):
    if not isinstance(value, bool):
        raise PfandbriefError("INVALID_BOOLEAN", f"{name} must be an explicit bool")
    return value


def iso_date(value, name):
    if isinstance(value, datetime):
        raise PfandbriefError("INVALID_DATE", f"{name} must be a date, not a timestamp")
    if isinstance(value, date):
        return value
    try:
        parsed = date.fromisoformat(value)
        if parsed.isoformat() != value:
            raise ValueError("noncanonical date")
        return parsed
    except (ValueError, TypeError) as exc:
        raise PfandbriefError("INVALID_DATE", f"{name} must be YYYY-MM-DD") from exc


def input_fingerprint(data):
    """Fingerprint JSON-compatible inputs, not a cross-language floating point oracle."""

    def keys(obj):
        if isinstance(obj, dict):
            if any(not isinstance(k, str) or not k for k in obj):
                raise PfandbriefError(
                    "INVALID_SERIALIZATION", "mapping keys must be nonempty strings"
                )
            for v in obj.values():
                keys(v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                keys(v)

    keys(data)
    try:
        payload = json.dumps(
            data,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
    except (ValueError, TypeError) as exc:
        raise PfandbriefError(
            "INVALID_SERIALIZATION", "inputs must be finite JSON data"
        ) from exc
    return sha256(payload.encode("utf-8")).hexdigest()
