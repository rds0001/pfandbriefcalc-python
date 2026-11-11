"""Native offline Pfandbrief calculation tools. AGPL-3.0-only."""

from .core import CalcResult, PfandbriefError
from .finance import (
    year_fraction,
    adjust_date,
    coupon_schedule,
    contract_cashflows,
    discount_factors,
    present_value,
    bond_analytics,
    yield_to_maturity,
    accrued_interest,
)
from .stress import rate_shocks, fx_shock, stressed_fx_net
from .valuation import (
    annuity_factor,
    income_value,
    comparison_value,
    cost_value,
    ship_value_limit,
    aircraft_value_limit,
)
from .coverage import secured_amount, coverage_amounts, liquidity_gap
from .property import (
    indexed_administration_cost,
    operating_costs,
    linear_depreciation,
    construction_value_limit,
    property_value_check,
    foreign_perpetuity_value,
    valuation_review,
    property_parameter_check,
    small_loan_check,
)
from .controls import (
    select_rule_profile,
    assess_evidence,
    validate_allocations,
    register_snapshot,
)
from .pools import pool_coverage, pool_limits, pool_stress, liquidity_180
from .eligibility import (
    cover_amount,
    mortgage_terms_check,
    transport_loan_check,
    insurance_check,
    required_evidence,
)
from .portfolio import pool_requirements, analyze_pool
from .examples import example_pool, cashflow_example_pool
from .eu import (
    covered_bond_risk_weight,
    european_label,
    crr_pool_check,
    covered_bond_lcr,
    liquid_buffer_value,
)
from .events import (
    validate_register_entries,
    deferred_interest,
    interest_extension,
    extension_plan,
)
from .reporting import (
    pool_metrics,
    aggregate_positions,
    maturity_buckets,
    weighted_ltv,
    reconcile_totals,
    export_table,
)
from .advanced import (
    cashflow_scenarios,
    project_floating_coupons,
    effective_sensitivities,
    equivalent_cap_rate,
    ship_construction_value_check,
    transport_valuation_review,
)

__version__ = "0.1.1"
__all__ = [
    "CalcResult",
    "PfandbriefError",
    "annuity_factor",
    "income_value",
    "comparison_value",
    "cost_value",
    "ship_value_limit",
    "aircraft_value_limit",
    "secured_amount",
    "coverage_amounts",
    "liquidity_gap",
    "year_fraction",
    "adjust_date",
    "coupon_schedule",
    "contract_cashflows",
    "discount_factors",
    "present_value",
    "bond_analytics",
    "yield_to_maturity",
    "accrued_interest",
    "rate_shocks",
    "fx_shock",
    "stressed_fx_net",
    "indexed_administration_cost",
    "operating_costs",
    "linear_depreciation",
    "construction_value_limit",
    "property_value_check",
    "foreign_perpetuity_value",
    "valuation_review",
    "property_parameter_check",
    "small_loan_check",
    "select_rule_profile",
    "assess_evidence",
    "validate_allocations",
    "register_snapshot",
    "pool_coverage",
    "pool_limits",
    "pool_stress",
    "liquidity_180",
    "cover_amount",
    "mortgage_terms_check",
    "transport_loan_check",
    "insurance_check",
    "required_evidence",
    "pool_requirements",
    "analyze_pool",
    "example_pool",
    "cashflow_example_pool",
    "covered_bond_risk_weight",
    "european_label",
    "crr_pool_check",
    "covered_bond_lcr",
    "liquid_buffer_value",
    "validate_register_entries",
    "deferred_interest",
    "interest_extension",
    "extension_plan",
    "pool_metrics",
    "aggregate_positions",
    "maturity_buckets",
    "weighted_ltv",
    "reconcile_totals",
    "export_table",
    "cashflow_scenarios",
    "project_floating_coupons",
    "effective_sensitivities",
    "equivalent_cap_rate",
    "ship_construction_value_check",
    "transport_valuation_review",
]
