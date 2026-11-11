"""Property valuation controls. SPDX-License-Identifier: AGPL-3.0-only."""

from decimal import Decimal
from fractions import Fraction
from .core import CalcResult, PfandbriefError, choice, flag, number, iso_date
from .finance import _month_date

PROPERTY_PARAMETERS = {
    "residential": (80, 0),
    "office": (60, 0),
    "business": (60, 0),
    "department_store": (40, 0.005),
    "shopping_center": (40, 0.005),
    "hotel": (40, 0.005),
    "agricultural": (40, 0.005),
    "clinic": (40, 0.005),
    "rehabilitation": (40, 0.005),
    "care_home": (40, 0.005),
    "logistics": (40, 0.005),
    "production": (40, 0.01),
    "parking": (40, 0.005),
    "leisure": (30, 0.005),
    "specialty_market": (30, 0.005),
    "consumer_market": (30, 0.005),
    "petrol_station": (30, 0.005),
}


def property_parameter_check(
    property_use,
    remaining_life,
    capitalization_rate,
    notified_base_rate,
    *,
    prime_reduction=0.0,
    prime_conditions=None,
    prime_reason=None,
):
    """Domestic annex life/rate controls; the official effective base rate is supplied."""
    choice(property_use, "property_use", PROPERTY_PARAMETERS)
    life = number(remaining_life, "remaining_life", 0)
    rate = number(capitalization_rate, "capitalization_rate", 0, strict_min=True)
    residential = property_use == "residential"
    base = number(
        notified_base_rate,
        "notified_base_rate",
        0.035 if residential else 0.045,
        0.055 if residential else 0.065,
    )
    reduction = number(prime_reduction, "prime_reduction", 0, 0.005)
    maximum, supplement = PROPERTY_PARAMETERS[property_use]
    conditions = (
        "urban_location",
        "preferred_site",
        "infrastructure",
        "concept",
        "equipment",
        "construction",
        "marketability",
        "condition",
    )
    missing = []
    failed = []
    if reduction:
        allowed = {
            "residential",
            "office",
            "business",
            "department_store",
            "shopping_center",
            "specialty_market",
            "consumer_market",
            "logistics",
        }
        if property_use not in allowed:
            failed.append("prime_use_not_permitted")
        if prime_conditions is None:
            missing.append("eight_prime_conditions")
        elif not isinstance(prime_conditions, dict) or set(prime_conditions) != set(
            conditions
        ):
            raise PfandbriefError(
                "MISSING_FIELD", "provide all eight named prime conditions"
            )
        else:
            for k in conditions:
                if not flag(prime_conditions[k], k):
                    failed.append(k)
        if not isinstance(prime_reason, str) or not prime_reason.strip():
            missing.append("prime_reason")
    elif prime_conditions is not None or prime_reason is not None:
        raise PfandbriefError(
            "NOT_APPLICABLE", "prime evidence supplied without reduction"
        )
    minimum = base + supplement - reduction
    if life > maximum:
        failed.append("remaining_life")
    if rate < minimum:
        failed.append("capitalization_rate")
    decision = (
        "FAILED" if failed else ("REVIEW_REQUIRED" if missing else "CHECKS_PASSED")
    )
    return CalcResult(
        decision,
        "property_parameter_check",
        ("BelWertV §12; Anlagen2,3",),
        "decision",
        details={
            "maximum_life": maximum,
            "minimum_rate": minimum,
            "supplement": supplement,
            "failed_checks": failed,
            "missing_evidence": missing,
        },
        limitations=(
            "Official notice, effective date, market derivation and prime evidence remain externally verified inputs",
        ),
    )


def small_loan_check(
    loan_amount,
    prior_liens,
    commercial_income_share,
    domestic_residential,
    inspection_mode,
    *,
    years_since_inspection=None,
    known_object=False,
    comparable_object=False,
    prefabricated_known=False,
    remaining_life=None,
    video_complete=False,
    video_documented=False,
    valuation_haircut=0.0,
    essential_parameters_known=False,
    building_age=None,
    reason_documented=False,
):
    """§24 amount/use and inspection-exception checks; no waiver of other valuation duties."""
    loan = number(loan_amount, "loan_amount", 0)
    prior = number(prior_liens, "prior_liens", 0)
    share = number(commercial_income_share, "commercial_income_share", 0, 1)
    choice(
        inspection_mode,
        "inspection_mode",
        ("full", "known", "comparable", "prefabricated", "video", "exterior_only"),
    )
    for k, v in locals().copy().items():
        if k in (
            "domestic_residential",
            "known_object",
            "comparable_object",
            "prefabricated_known",
            "video_complete",
            "video_documented",
            "essential_parameters_known",
            "reason_documented",
        ):
            flag(v, k)
    h = number(valuation_haircut, "valuation_haircut", 0, 1)
    failures = []
    if not domestic_residential:
        failures.append("domestic_residential")
    if loan + prior > 600000:
        failures.append("amount_limit")
    if share > 1 / 3:
        failures.append("commercial_income_share")
    if inspection_mode != "full" and not reason_documented:
        failures.append("inspection_reason")
    if inspection_mode in ("known", "comparable"):
        elapsed = number(years_since_inspection, "years_since_inspection", 0)
        if elapsed > 2:
            failures.append("inspection_age")
        if not (known_object if inspection_mode == "known" else comparable_object):
            failures.append("inspection_relationship")
    elif inspection_mode == "prefabricated":
        if not prefabricated_known:
            failures.append("site_and_type_known")
    elif inspection_mode == "video":
        life = number(remaining_life, "remaining_life", 0)
        if life < 40 or not video_complete or not video_documented or h < 0.05:
            failures.append("video_conditions")
    elif inspection_mode == "exterior_only":
        age = number(building_age, "building_age", 0)
        if not essential_parameters_known or (age > 10 and h < 0.10):
            failures.append("exterior_only_conditions")
    return CalcResult(
        not failures,
        "small_loan_check",
        ("BelWertV §24(1),(3),(3a)",),
        "boolean",
        details={
            "failed_checks": failures,
            "amount_including_prior_liens": loan + prior,
        },
        limitations=(
            "Qualification, independence, simplified valuation, sampling and exception evidence remain required",
        ),
    )


def indexed_administration_cost(unit_type, october_cpi_previous_year, october_cpi_2001):
    """Per-unit annual residential minimum; CPI series must have the same index base."""
    bases = {"dwelling": 230, "condominium": 275, "garage": 30}
    choice(unit_type, "unit_type", bases)
    now = number(
        october_cpi_previous_year, "october_cpi_previous_year", 0, strict_min=True
    )
    then = number(october_cpi_2001, "october_cpi_2001", 0, strict_min=True)
    texts = [format(x, ".14e") for x in (now, then)]
    if any(float(t) != x for t, x in zip(texts, (now, then))):
        raise PfandbriefError(
            "INDEX_PRECISION",
            "CPI values support at most 15 significant decimal digits",
        )
    raw = bases[unit_type] * Fraction(Decimal(texts[0])) / Fraction(Decimal(texts[1]))
    rounded = (2 * raw.numerator + raw.denominator) // (2 * raw.denominator)
    try:
        amount = float(rounded)
    except OverflowError as exc:
        raise PfandbriefError(
            "NUMERIC_RANGE", "nonfinite index calculation result"
        ) from exc
    return CalcResult(
        amount,
        "indexed_administration_cost",
        ("BelWertV Anlage1; ImmoWertV Anlage3",),
        "EUR_per_unit_year",
        details={"base_amount": bases[unit_type], "index_ratio": now / then},
        limitations=(
            "CPI period, common index base and official data source require external verification",
        ),
    )


def operating_costs(
    gross_income,
    construction_cost,
    use,
    maintenance_class,
    modernization_class,
    estimates,
    actual_total,
    *,
    residential_administration_floor=None,
):
    """Component minima, 15% aggregate floor and actual total; all costs annual."""
    gross = number(gross_income, "gross_income", 0)
    construction = number(construction_cost, "construction_cost", 0)
    choice(use, "use", ("residential", "commercial"))
    mr = {"simple": 0.008, "medium": 0.005, "high": 0.004}
    modern = {"none": 0, "low": 0.002, "medium": 0.005, "high": 0.0075}
    choice(maintenance_class, "maintenance_class", mr)
    choice(modernization_class, "modernization_class", modern)
    keys = {"administration", "maintenance", "rent_loss", "operating", "modernization"}
    if not isinstance(estimates, dict) or set(estimates) != keys:
        raise PfandbriefError(
            "MISSING_FIELD", "provide exactly the five annual expense estimates"
        )
    estimates = {k: number(v, k, 0) for k, v in estimates.items()}
    actual = number(actual_total, "actual_total", 0)
    if use == "residential":
        admin = number(
            residential_administration_floor, "residential_administration_floor", 0
        )
        if maintenance_class != "medium":
            raise PfandbriefError(
                "INVALID_CHOICE",
                "residential maintenance requires the medium statutory floor",
            )
    else:
        if residential_administration_floor is not None:
            raise PfandbriefError(
                "NOT_APPLICABLE", "residential floor does not apply to commercial use"
            )
        admin = 0.01 * gross
    minima = {
        "administration": admin,
        "maintenance": construction * mr[maintenance_class],
        "rent_loss": gross * (0.02 if use == "residential" else 0.04),
        "operating": 0,
        "modernization": construction * modern[modernization_class],
    }
    applied = {k: max(estimates[k], minima[k]) for k in sorted(keys)}
    core = sum(applied[k] for k in ("administration", "maintenance", "rent_loss"))
    floor_extra = max(0, 0.15 * gross - core)
    before_actual = core + floor_extra + applied["operating"] + applied["modernization"]
    total = max(before_actual, actual)
    return CalcResult(
        total,
        "operating_costs",
        ("BelWertV §11; Anlage1",),
        "currency_per_year",
        details={
            "component_minima": minima,
            "applied_components": applied,
            "aggregate_floor_addition": floor_extra,
            "actual_total_addition": total - before_actual,
            "net_income": gross - total,
        },
        limitations=(
            "Acute rent default is a separate value deduction; risk classification requires appraisal",
        ),
    )


def linear_depreciation(remaining_life, total_life):
    """Linear age depreciation as one minus remaining life divided by total life."""
    n = number(remaining_life, "remaining_life", 0)
    g = number(total_life, "total_life", 0, strict_min=True)
    if n > g:
        raise PfandbriefError("OUT_OF_RANGE", "remaining life exceeds total life")
    return CalcResult(1 - n / g, "linear_depreciation", ("BelWertV §17",), "fraction")


def construction_value_limit(
    land_value,
    finished_cost_value,
    finished_income_value,
    progress,
    sustainability_deduction,
):
    """Property construction-stage value using confirmed progress and explicit deductions."""
    land = number(land_value, "land_value", 0)
    cost = number(finished_cost_value, "finished_cost_value", land)
    income = number(finished_income_value, "finished_income_value", land)
    progress = number(progress, "progress", 0, 1)
    deduction = number(sustainability_deduction, "sustainability_deduction", 0)
    raw = land + progress * min(cost - land, income - land)
    return CalcResult(
        raw - deduction,
        "construction_value_limit",
        ("BelWertV §4(4)",),
        "currency",
        details={"before_deduction": raw},
        limitations=(
            "Independent construction-progress evidence and market assessment remain required",
        ),
    )


def property_value_check(
    proposed_value,
    market_value,
    method,
    control_value,
    *,
    income_estimate=None,
    deductions=0.0,
    deductions_not_already_included,
    property_type="other",
    owner_occupation_suitability=None,
    rented=False,
    rental_deduction=None,
    comparable_count=None,
    qualified_model=None,
    sustainability_review=None,
):
    """Arithmetic bound and explicitly unresolved method evidence; no value-setting authority."""
    proposed = number(proposed_value, "proposed_value", 0)
    market = number(market_value, "market_value", 0)
    control = number(control_value, "control_value", 0)
    deductions = number(deductions, "deductions", 0)
    flag(deductions_not_already_included, "deductions_not_already_included")
    if deductions and not deductions_not_already_included:
        raise PfandbriefError(
            "DOUBLE_DEDUCTION", "do not deduct previously included adjustments twice"
        )
    choice(method, "method", ("income_standard", "owner_cost", "owner_comparison"))
    choice(
        property_type,
        "property_type",
        ("single_family", "duplex", "condominium", "other"),
    )
    pending = []
    failures = []
    review = False
    for name, value in (
        ("owner_occupation_suitability", owner_occupation_suitability),
        ("qualified_model", qualified_model),
        ("sustainability_review", sustainability_review),
    ):
        if value is not None:
            flag(value, name)
    flag(rented, "rented")
    if method == "income_standard":
        income = number(income_estimate, "income_estimate", 0)
        cap = min(income, market) - deductions
        review = control < 0.8 * income
        if review:
            if sustainability_review is None:
                pending.append("sustainability_review")
            elif not sustainability_review:
                failures.append("income_sustainability_not_confirmed")
    else:
        if income_estimate is not None:
            raise PfandbriefError(
                "NOT_APPLICABLE", "owner method does not consume income estimate"
            )
        if property_type == "other":
            failures.append("owner_method_object_type")
        if owner_occupation_suitability is None:
            pending.append("owner_occupation_suitability")
        elif not owner_occupation_suitability:
            failures.append("owner_occupation_suitability")
        if method == "owner_comparison" and property_type in (
            "single_family",
            "duplex",
        ):
            count = (
                0
                if comparable_count is None
                else number(comparable_count, "comparable_count", 0)
            )
            if count != int(count):
                raise PfandbriefError("OUT_OF_RANGE", "comparable_count must be whole")
            if count < 5 and qualified_model is not True:
                (pending if qualified_model is None else failures).append(
                    "five_comparables_or_qualified_model"
                )
        if rented and rental_deduction is None:
            pending.append("rental_deduction")
        rental = (
            0
            if rental_deduction is None
            else number(rental_deduction, "rental_deduction", 0)
        )
        if not rented and rental:
            raise PfandbriefError(
                "NOT_APPLICABLE", "rental deduction requires a rented property"
            )
        cap = min(control, market) - deductions - rental
    if proposed > cap:
        failures.append("proposed_value_above_limit")
    decision = (
        "FAILED" if failures else ("REVIEW_REQUIRED" if pending else "CHECKS_PASSED")
    )
    return CalcResult(
        decision,
        "property_value_check",
        ("BelWertV §4; PfandBG §16(2)",),
        "decision",
        details={
            "arithmetic_limit": cap,
            "sustainability_review_triggered": review,
            "missing_evidence": pending,
            "failed_checks": failures,
        },
        limitations=(
            "Supplied evidence flags are not authenticated; formal appraisal and value determination remain external",
        ),
    )


def foreign_perpetuity_value(
    net_income, rate, additional_depreciation, method_evidence
):
    """Foreign perpetuity value after an explicit compensating building-depreciation cost."""
    n = number(net_income, "net_income")
    z = number(rate, "rate", 0, strict_min=True)
    depreciation = number(
        additional_depreciation, "additional_depreciation", 0, strict_min=True
    )
    if not flag(method_evidence, "method_evidence"):
        raise PfandbriefError(
            "MISSING_EVIDENCE",
            "foreign perpetuity requires documented method conditions",
        )
    return CalcResult(
        (n - depreciation) / z,
        "foreign_perpetuity_value",
        ("BelWertV §25(4)",),
        "currency",
        details={"income_after_additional_depreciation": n - depreciation},
        limitations=(
            "Additional depreciation must adequately compensate the actual shorter economic life",
        ),
    )


def valuation_review(
    as_of,
    last_monitoring,
    material_deterioration,
    material_arrears_days,
    *,
    owner_occupied_residential=False,
):
    """Property annual-monitoring deadline and material-deterioration or arrears triggers."""
    day = iso_date(as_of, "as_of")
    last = iso_date(last_monitoring, "last_monitoring")
    if last > day:
        raise PfandbriefError("DATE_ORDER", "monitoring cannot be in the future")
    flag(material_deterioration, "material_deterioration")
    flag(owner_occupied_residential, "owner_occupied_residential")
    arrears = number(material_arrears_days, "material_arrears_days", 0)
    if arrears != int(arrears):
        raise PfandbriefError("OUT_OF_RANGE", "arrears days must be whole")
    due = _month_date(last, 12, False)
    review = material_deterioration or (
        arrears >= 90 and not owner_occupied_residential
    )
    return CalcResult(
        review or day >= due,
        "valuation_review",
        ("BelWertV §26",),
        "boolean",
        details={
            "monitoring_due": day >= due,
            "monitoring_deadline": due.isoformat(),
            "review_required": review,
        },
        limitations=(
            "Further review obligations may apply; materiality is an evidenced input",
        ),
    )
