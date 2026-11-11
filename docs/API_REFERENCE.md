# pfandbriefcalc API reference

Native Python and R expose the same calculation functions. Rates are decimals; values are unrounded currency amounts unless stated otherwise. Every function returns a calculation result with value, method, sources, unit, status, details and limitations. CALCULATED describes successful execution; the decision in value/details may still be FAILED or INCOMPLETE.

Record schemas are in [DATA_CONTRACTS.md](DATA_CONTRACTS.md); worked usage is in [HANDBOOK.md](HANDBOOK.md).

## annuity_factor

Annual end-of-period annuity multiplier; rate=0 is a mathematical limit.

```python
annuity_factor(rate, years)
```

```r
annuity_factor(rate, years)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `rate` | Rate as a decimal, for example 0.05 for 5 percent. Its compounding and admissible bounds follow the selected method. |
| `years` | Explicit duration or age in years. This is not a date or a number of days; method-specific age/life limits are checked. |

Method contract: `STARTKERN.md`.

Limitations: No approval of the supplied capitalization rate

```python
annuity_factor(0.05, 20)
```

## income_value

Income approach including §13 alternatives; returns unrounded monetary value.

The net income must already include adequate operating-cost deductions.
For a remaining life below 30 years explicitly select capitalize_land or
deduct_demolition. Nonpositive building income requires land_release_years.

```python
income_value(net_income, land_value, rate, years, *, short_life_method=None, demolition_costs=None, land_release_years=None)
```

```r
income_value(net_income, land_value, rate, years, short_life_method = NULL, demolition_costs = NULL, land_release_years = NULL)
```

For positive building income N-zB and life>=30: B+(N-zB)*annuity_factor(z,n). For life<30 choose capitalize_land (N*factor) or deduct_demolition. Nonpositive building income needs both demolition_costs and land_release_years and yields the discounted land-only amount.

| Parameter | Meaning |
|---|---|
| `net_income` | Sustainable annual income in currency units; net_income already reflects the deductions required by the chosen method, unless explicitly used to solve an equivalent rate. |
| `land_value` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `rate` | Rate as a decimal, for example 0.05 for 5 percent. Its compounding and admissible bounds follow the selected method. |
| `years` | Explicit duration or age in years. This is not a date or a number of days; method-specific age/life limits are checked. |
| `short_life_method` | For remaining life below 30 years: capitalize_land or, where supported, deduct_demolition. Standard long-life valuation rejects this argument. |
| `demolition_costs` | Nonnegative future demolition amount; land_release_years supplies its discount horizon in the selected short-life branch. |
| `land_release_years` | Explicit duration or age in years. This is not a date or a number of days; method-specific age/life limits are checked. |

Method contract: `STARTKERN.md`.

Limitations: Rate, net income, land estimate and valuation evidence are supplied inputs Not a binding lending-value determination

```python
income_value(10000, 50000, 0.05, 40)
```

## comparison_value

Apply the §19 minimum haircut to an independently established comparison value.

```python
comparison_value(base_value, haircut=0.1)
```

```r
comparison_value(base_value, haircut = 0.1)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `base_value` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `haircut` | Explicit value-reduction fraction. The function applies its documented statutory minimum; a missing input is not a zero haircut. |

Method contract: `STARTKERN.md`.

Limitations: Comparable selection and adjustments require independent evidence

## cost_value

Cost-value arithmetic with explicit depreciation and separately assessed deductions.

```python
cost_value(construction_value, land_value, age_depreciation, *, safety_haircut=0.1, incidental_rate=0.0, other_deductions=0.0, demolition_present_value=0.0)
```

```r
cost_value(construction_value, land_value, age_depreciation, safety_haircut = 0.1, incidental_rate = 0, 
    other_deductions = 0, demolition_present_value = 0)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `construction_value` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `land_value` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `age_depreciation` | Explicit accumulated depreciation fraction, between zero and one, applied after the defined construction-value adjustments. |
| `safety_haircut` | Explicit value-reduction fraction. The function applies its documented statutory minimum; a missing input is not a zero haircut. |
| `incidental_rate` | Eligible incidental-cost fraction, at most 0.20, applied to the safety-adjusted construction value. |
| `other_deductions` | Explicit monetary deduction not already included in the input value. demolition_present_value must already be discounted. |
| `demolition_present_value` | Explicit monetary deduction not already included in the input value. demolition_present_value must already be discounted. |

Method contract: `STARTKERN.md`.

Limitations: §14 demolition assessment for short remaining life remains required Explicit depreciation must follow the documented age model

## ship_value_limit

Ship value upper bound; not the valuation or approval of an alternative method.

```python
ship_value_limit(current_market_value, average_market_value, price, history_years, *, extra_haircut=0.0)
```

```r
ship_value_limit(current_market_value, average_market_value, price, history_years, extra_haircut = 0)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `current_market_value` | Monetary market/value/price input. A missing transport market value is None/NULL only in a documented alternative branch; bond price is a dirty amount price. |
| `average_market_value` | Monetary market/value/price input. A missing transport market value is None/NULL only in a documented alternative branch; bond price is a dirty amount price. |
| `price` | Monetary market/value/price input. A missing transport market value is None/NULL only in a documented alternative branch; bond price is a dirty amount price. |
| `history_years` | Whole number of years of usable comparable-market history, from 0 through 10; missing averages require zero. |
| `extra_haircut` | Explicit value-reduction fraction. The function applies its documented statutory minimum; a missing input is not a zero haircut. |

Method contract: `STARTKERN.md`.

Limitations: Upper limit only; a sustainable appraised value must be established separately

## aircraft_value_limit

Aircraft upper limits, preserving available independent bounds.

```python
aircraft_value_limit(current_market_value, average_market_value, balanced_value, history_years)
```

```r
aircraft_value_limit(current_market_value, average_market_value, balanced_value, history_years)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `current_market_value` | Monetary market/value/price input. A missing transport market value is None/NULL only in a documented alternative branch; bond price is a dirty amount price. |
| `average_market_value` | Monetary market/value/price input. A missing transport market value is None/NULL only in a documented alternative branch; bond price is a dirty amount price. |
| `balanced_value` | Monetary market/value/price input. A missing transport market value is None/NULL only in a documented alternative branch; bond price is a dirty amount price. |
| `history_years` | Whole number of years of usable comparable-market history, from 0 through 10; missing averages require zero. |

Method contract: `STARTKERN.md`.

Limitations: Upper limit only; estimates, sustainable value and method evidence are external

## secured_amount

Allocate one explicitly established seniority slice; no legal eligibility decision.

```python
secured_amount(claim, lien, lending_value, prior_claims, assigned_amount, lending_limit)
```

```r
secured_amount(claim, lien, lending_value, prior_claims, assigned_amount, lending_limit)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `claim` | Nonnegative monetary principal or claim in the calculation currency; no implicit conversion or scaling is performed. |
| `lien` | Amount of the institution's own legally effective collateral right, excluding separately specified prior claims. |
| `lending_value` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `prior_claims` | Explicit relevant prior-ranking claims in currency units. Equal-ranking slices must first be allocated consistently with the legal ranking agreement. |
| `assigned_amount` | Explicit amount assigned to this cover register/tranche, in the same currency as the claim. |
| `lending_limit` | Eligible first-rank fraction of lending value, expressed as a decimal. Any departure from the regular 0.60 requires an applicable evidenced rule or exception. |

Method contract: `STARTKERN.md`.

Limitations: Requires separately established eligibility, legal rank and unique allocation

## coverage_amounts

One homogeneous coverage view; does not certify separate qualifying OC assets.

```python
coverage_amounts(assets, liabilities, required_overcollateralization)
```

```r
coverage_amounts(assets, liabilities, required_overcollateralization)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `assets` | Homogeneous amounts for coverage_amounts, or typed record tables for pool methods. See the per-function table contracts in DATA_CONTRACTS.md. |
| `liabilities` | Homogeneous amounts for coverage_amounts, or typed record tables for pool methods. See the per-function table contracts in DATA_CONTRACTS.md. |
| `required_overcollateralization` | Required or observed overcollateralization fraction above liabilities, for example 0.02 for 2 percent. Not the asset/liability ratio 1.02. |

Method contract: `STARTKERN.md`.

Limitations: No eligibility, separate OC allocation or overall regulatory approval

## liquidity_gap

Worst cumulative daily deficit; vectors contain every day of the chosen horizon.

```python
liquidity_gap(inflows, outflows, buffer)
```

```r
liquidity_gap(inflows, outflows, buffer)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `inflows` | Nonnegative daily amount vectors, including days with zero flows, in one currency and with equal length. |
| `outflows` | Nonnegative daily amount vectors, including days with zero flows, in one currency and with equal length. |
| `buffer` | Already qualified and valued liquidity buffer amount in the same currency as the daily flows. |

Method contract: `STARTKERN.md`.

Limitations: Caller must supply the full regulatory horizon and qualified valued buffer

## year_fraction

ACT/365F, ACT/360, 30E/360 or ACT/ACT-ISDA; no implicit convention.

```python
year_fraction(start, end, convention)
```

```r
year_fraction(start, end, convention)
```

Conventions: ACT/365F, ACT/360, 30E/360 European and ACT/ACT-ISDA. ACT/ACT splits the interval at calendar-year boundaries. Dates are unadjusted accrual boundaries.

| Parameter | Meaning |
|---|---|
| `start` | Explicit calendar date in YYYY-MM-DD (or an R Date). The argument name identifies the contractual boundary; intervals must be chronological. |
| `end` | Explicit calendar date in YYYY-MM-DD (or an R Date). The argument name identifies the contractual boundary; intervals must be chronological. |
| `convention` | Day-count or business-day convention, according to the function; accepted identifiers are stated in the function details. |

Method contract: `CASHFLOWS_RISIKEN.md`.

```python
year_fraction("2024-02-28", "2024-03-01", "ACT/ACT-ISDA")
```

## adjust_date

Business date using explicit holidays and Saturday/Sunday weekends.

```python
adjust_date(day, convention, holidays)
```

```r
adjust_date(day, convention, holidays)
```

Conventions: unadjusted, following, modified_following and preceding. The holiday set is explicitly supplied, not inferred from a country name.

| Parameter | Meaning |
|---|---|
| `day` | Explicit calendar date in YYYY-MM-DD (or an R Date). The argument name identifies the contractual boundary; intervals must be chronological. |
| `convention` | Day-count or business-day convention, according to the function; accepted identifiers are stated in the function details. |
| `holidays` | Explicit sequence of holiday dates; an empty sequence means weekends only. No calendar is downloaded. |

Method contract: `CASHFLOWS_RISIKEN.md`.

## coupon_schedule

Backward anchored schedule with optional short first stub; no adjusted accruals.

```python
coupon_schedule(start, maturity, frequency, day_count, business_day, holidays, *, end_of_month=False)
```

```r
coupon_schedule(start, maturity, frequency, day_count, business_day, holidays, end_of_month = FALSE)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `start` | Explicit calendar date in YYYY-MM-DD (or an R Date). The argument name identifies the contractual boundary; intervals must be chronological. |
| `maturity` | Explicit calendar date in YYYY-MM-DD (or an R Date). The argument name identifies the contractual boundary; intervals must be chronological. |
| `frequency` | Payments or yield compounding periods per year. Coupon schedules accept 1, 2, 4 or 12. |
| `day_count` | ACT/365F, ACT/360, 30E/360 (European, not ISDA-February), or ACT/ACT-ISDA. Fractions are unrounded. |
| `business_day` | unadjusted, following, modified_following, or preceding. Saturday/Sunday and explicitly supplied holidays are nonbusiness days. |
| `holidays` | Explicit sequence of holiday dates; an empty sequence means weekends only. No calendar is downloaded. |
| `end_of_month` | Boolean month-end anchoring. When true, the supplied maturity must itself be a calendar month end. |

Method contract: `CASHFLOWS_RISIKEN.md`.

## contract_cashflows

Explicit period rates and repayments; remaining principal repaid at maturity.

```python
contract_cashflows(schedule, principal, coupon_rates, amortizations)
```

```r
contract_cashflows(schedule, principal, coupon_rates, amortizations)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `schedule` | Nonempty period records start, end, payment_date, year_fraction, usually returned by coupon_schedule. |
| `principal` | Nonnegative monetary principal or claim in the calculation currency; no implicit conversion or scaling is performed. |
| `coupon_rates` | One decimal contractual coupon rate per period, including supplied fixings or separately projected floating rates. |
| `amortizations` | One nonnegative scheduled repayment per period. The final period repays all remaining principal; over-repayment is rejected. |

Method contract: `CASHFLOWS_RISIKEN.md`.

Limitations: Rates, resets, option exercise and day-count fractions are explicit contractual inputs

## discount_factors

Continuous zero rates; linear zero interpolation; optional explicit flat extrapolation.

```python
discount_factors(times, curve_times, zero_rates, *, extrapolation='error', spread=0.0)
```

```r
discount_factors(times, curve_times, zero_rates, extrapolation = "error", spread = 0)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `times` | Explicit year coordinates relative to the valuation date. Curve nodes must be strictly increasing; floating-coupon starts/ends/resets follow the documented in-advance convention. |
| `curve_times` | Explicit year coordinates relative to the valuation date. Curve nodes must be strictly increasing; floating-coupon starts/ends/resets follow the documented in-advance convention. |
| `zero_rates` | Continuously compounded decimal zero rates at the supplied curve nodes. Rates may be negative; no implicit zero floor is imposed. |
| `extrapolation` | error rejects cashflows outside the curve; flat_zero explicitly extends the endpoint zero rates. |
| `spread` | Explicit decimal spread. spread shifts the continuous discount curve; margin is added to the floating index coupon. |

Method contract: `CASHFLOWS_RISIKEN.md`.

## present_value

Signed deterministic cashflows in a single currency.

```python
present_value(amounts, times, curve_times, zero_rates, *, extrapolation='error', spread=0.0)
```

```r
present_value(amounts, times, curve_times, zero_rates, extrapolation = "error", spread = 0)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `amounts` | Explicit cashflow amounts in one currency, matching times. Signed cashflows are accepted by PV methods; bond yield analytics require nonnegative future payments. |
| `times` | Explicit year coordinates relative to the valuation date. Curve nodes must be strictly increasing; floating-coupon starts/ends/resets follow the documented in-advance convention. |
| `curve_times` | Explicit year coordinates relative to the valuation date. Curve nodes must be strictly increasing; floating-coupon starts/ends/resets follow the documented in-advance convention. |
| `zero_rates` | Continuously compounded decimal zero rates at the supplied curve nodes. Rates may be negative; no implicit zero floor is imposed. |
| `extrapolation` | error rejects cashflows outside the curve; flat_zero explicitly extends the endpoint zero rates. |
| `spread` | Explicit decimal spread. spread shifts the continuous discount curve; margin is added to the floating index coupon. |

Method contract: `CASHFLOWS_RISIKEN.md`.

Limitations: Does not value embedded options or replace independent derivative market prices

## bond_analytics

Amount prices, Macaulay/modified duration and convexity; positive cashflows.

```python
bond_analytics(amounts, times, yield_rate, frequency, *, accrued_interest=0.0)
```

```r
bond_analytics(amounts, times, yield_rate, frequency, accrued_interest = 0)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `amounts` | Explicit cashflow amounts in one currency, matching times. Signed cashflows are accepted by PV methods; bond yield analytics require nonnegative future payments. |
| `times` | Explicit year coordinates relative to the valuation date. Curve nodes must be strictly increasing; floating-coupon starts/ends/resets follow the documented in-advance convention. |
| `yield_rate` | Rate as a decimal, for example 0.05 for 5 percent. Its compounding and admissible bounds follow the selected method. |
| `frequency` | Payments or yield compounding periods per year. Coupon schedules accept 1, 2, 4 or 12. |
| `accrued_interest` | Explicit accrued interest amount subtracted from the dirty amount price to obtain the clean amount price. |

Method contract: `CASHFLOWS_RISIKEN.md`.

Limitations: Deterministic analyst model; prices are amounts, not per-100 quotations

## yield_to_maturity

Bracketed monotone yield solver with explicit bounds and no silent fallback.

```python
yield_to_maturity(price, amounts, times, frequency, lower, upper, *, tolerance=1e-12, max_iterations=256)
```

```r
yield_to_maturity(price, amounts, times, frequency, lower, upper, tolerance = 1e-12, max_iterations = 256)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `price` | Monetary market/value/price input. A missing transport market value is None/NULL only in a documented alternative branch; bond price is a dirty amount price. |
| `amounts` | Explicit cashflow amounts in one currency, matching times. Signed cashflows are accepted by PV methods; bond yield analytics require nonnegative future payments. |
| `times` | Explicit year coordinates relative to the valuation date. Curve nodes must be strictly increasing; floating-coupon starts/ends/resets follow the documented in-advance convention. |
| `frequency` | Payments or yield compounding periods per year. Coupon schedules accept 1, 2, 4 or 12. |
| `lower` | Explicit numerical search bracket. The function rejects an unbracketed target and never silently expands the interval. |
| `upper` | Explicit numerical search bracket. The function rejects an unbracketed target and never silently expands the interval. |
| `tolerance` | Positive convergence tolerance under the function's documented price/value residual convention. |
| `max_iterations` | Positive whole-number iteration limit; failure to converge raises NO_CONVERGENCE. |

Method contract: `CASHFLOWS_RISIKEN.md`.

## accrued_interest

Amount accrued from unadjusted coupon start; no ex-coupon convention assumed.

```python
accrued_interest(principal, coupon_rate, period_start, settlement, period_end, day_count)
```

```r
accrued_interest(principal, coupon_rate, period_start, settlement, period_end, day_count)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `principal` | Nonnegative monetary principal or claim in the calculation currency; no implicit conversion or scaling is performed. |
| `coupon_rate` | Rate as a decimal, for example 0.05 for 5 percent. Its compounding and admissible bounds follow the selected method. |
| `period_start` | Explicit calendar date in YYYY-MM-DD (or an R Date). The argument name identifies the contractual boundary; intervals must be chronological. |
| `settlement` | Explicit calendar date in YYYY-MM-DD (or an R Date). The argument name identifies the contractual boundary; intervals must be chronological. |
| `period_end` | Explicit calendar date in YYYY-MM-DD (or an R Date). The argument name identifies the contractual boundary; intervals must be chronological. |
| `day_count` | ACT/365F, ACT/360, 30E/360 (European, not ISDA-February), or ACT/ACT-ISDA. Fractions are unrounded. |

Method contract: `CASHFLOWS_RISIKEN.md`.

Limitations: No ex-coupon period or detached-coupon adjustment

## rate_shocks

Decimal up/down shocks. Dynamic history: 250 rows, columns correspond to tenors.

```python
rate_shocks(current_rates, *, method, tenors=None, history=None, ddof=1)
```

```r
rate_shocks(current_rates, method, tenors = NULL, history = NULL, ddof = 1)
```

method is static or dynamic. Static shocks are +/-0.025. Dynamic history needs 250 rows and at least seven nodes including 1/12,1,2,5,7,10,15 years. A nonpositive historical rate anywhere selects absolute changes for the entire currency curve; otherwise log changes are used. The shift has a 0.01 minimum.

| Parameter | Meaning |
|---|---|
| `current_rates` | Continuously compounded decimal zero rates at the supplied curve nodes. Rates may be negative; no implicit zero floor is imposed. |
| `method` | Explicit method selector; supported choices are listed in the function-specific details. No silent fallback to an alternative regulatory method. |
| `tenors` | Explicit year coordinates relative to the valuation date. Curve nodes must be strictly increasing; floating-coupon starts/ends/resets follow the documented in-advance convention. |
| `history` | For dynamic stress: exactly 250 observations. Rate history is a row-by-tenor table; FX history is a positive numeric vector. |
| `ddof` | Standard-deviation divisor correction, 0 or 1; the default 1 uses the sample divisor. This explicit statistical convention is retained in output. |

Method contract: `CASHFLOWS_RISIKEN.md`.

Limitations: Historical bank-day calendar, method continuity and approvals require evidence

## fx_shock

Relative FX shock. Explicit country group; no built-in mutable country list.

```python
fx_shock(*, method, currency_group=None, history=None, other_haircut=None, ddof=1)
```

```r
fx_shock(method, currency_group = NULL, history = NULL, other_haircut = NULL, ddof = 1)
```

method is static or dynamic. Static group haircuts are 0.10,0.20,or explicit OTHER>=0.25. Dynamic uses log changes of 250 positive FX observations, 2.33*sqrt(125) and the explicit ddof convention.

| Parameter | Meaning |
|---|---|
| `method` | Explicit method selector; supported choices are listed in the function-specific details. No silent fallback to an alternative regulatory method. |
| `currency_group` | Static FX class EU_EEA_CH, US_CA_UK_JP, or OTHER. Country/currency classification is a supplied, separately evidenced fact. |
| `history` | For dynamic stress: exactly 250 observations. Rate history is a row-by-tenor table; FX history is a positive numeric vector. |
| `other_haircut` | Explicit static OTHER-currency haircut, at least 0.25. Not used for the other static classes or dynamic FX stress. |
| `ddof` | Standard-deviation divisor correction, 0 or 1; the default 1 uses the sample divisor. This explicit statistical convention is retained in output. |

Method contract: `CASHFLOWS_RISIKEN.md`.

## stressed_fx_net

Adverse EUR value after currency-level asset/liability netting.

```python
stressed_fx_net(net_amount, eur_per_unit, shock)
```

```r
stressed_fx_net(net_amount, eur_per_unit, shock)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `net_amount` | Signed net asset minus liability present value in one foreign currency, after interest-rate stress. |
| `eur_per_unit` | Positive spot EUR value of one foreign-currency unit; reciprocal quotations are not inferred. |
| `shock` | Nonnegative relative adverse FX shock applied to the absolute net currency exposure. |

Method contract: `CASHFLOWS_RISIKEN.md`.

## indexed_administration_cost

Per-unit annual residential minimum; CPI series must have the same index base.

```python
indexed_administration_cost(unit_type, october_cpi_previous_year, october_cpi_2001)
```

```r
indexed_administration_cost(unit_type, october_cpi_previous_year, october_cpi_2001)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `unit_type` | dwelling, condominium, or garage for the applicable indexed annual administration-cost base. |
| `october_cpi_previous_year` | Positive compatible October consumer-price index values for the prior year and 2001; no index series is fetched. |
| `october_cpi_2001` | Positive compatible October consumer-price index values for the prior year and 2001; no index series is fetched. |

Method contract: `BEWERTUNG_ERWEITERT.md`.

Limitations: CPI period, common index base and official data source require external verification

## operating_costs

Component minima, 15% aggregate floor and actual total; all costs annual.

```python
operating_costs(gross_income, construction_cost, use, maintenance_class, modernization_class, estimates, actual_total, *, residential_administration_floor=None)
```

```r
operating_costs(gross_income, construction_cost, use, maintenance_class, modernization_class, estimates, actual_total, 
    residential_administration_floor = NULL)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `gross_income` | Sustainable annual income in currency units; net_income already reflects the deductions required by the chosen method, unless explicitly used to solve an equivalent rate. |
| `construction_cost` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `use` | residential or commercial; determines the applicable operating-cost floors. |
| `maintenance_class` | simple, medium, or high construction/equipment class for the statutory maintenance-cost rate. |
| `modernization_class` | none, low, medium, or high modernization risk, as explicitly appraised. |
| `estimates` | Mapping of five annual estimates: administration, maintenance, rent_loss, operating, modernization; amounts use one currency. |
| `actual_total` | Actual annual total operating costs, used as an additional minimum rather than silently discarded. |
| `residential_administration_floor` | Explicit annual residential administration-cost floor, commonly assembled using indexed_administration_cost and the number of units. |

Method contract: `BEWERTUNG_ERWEITERT.md`.

Limitations: Acute rent default is a separate value deduction; risk classification requires appraisal

## linear_depreciation

Linear age depreciation as one minus remaining life divided by total life.

```python
linear_depreciation(remaining_life, total_life)
```

```r
linear_depreciation(remaining_life, total_life)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `remaining_life` | Explicit duration or age in years. This is not a date or a number of days; method-specific age/life limits are checked. |
| `total_life` | Explicit duration or age in years. This is not a date or a number of days; method-specific age/life limits are checked. |

Method contract: `BEWERTUNG_ERWEITERT.md`.

## construction_value_limit

Property construction-stage value using confirmed progress and explicit deductions.

```python
construction_value_limit(land_value, finished_cost_value, finished_income_value, progress, sustainability_deduction)
```

```r
construction_value_limit(land_value, finished_cost_value, finished_income_value, progress, sustainability_deduction)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `land_value` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `finished_cost_value` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `finished_income_value` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `progress` | Confirmed construction progress fraction between zero and one; object-specific sustainability deductions remain separate. |
| `sustainability_deduction` | Explicit monetary deduction not already included in the input value. demolition_present_value must already be discounted. |

Method contract: `BEWERTUNG_ERWEITERT.md`.

Limitations: Independent construction-progress evidence and market assessment remain required

## property_value_check

Arithmetic bound and explicitly unresolved method evidence; no value-setting authority.

```python
property_value_check(proposed_value, market_value, method, control_value, *, income_estimate=None, deductions=0.0, deductions_not_already_included, property_type='other', owner_occupation_suitability=None, rented=False, rental_deduction=None, comparable_count=None, qualified_model=None, sustainability_review=None)
```

```r
property_value_check(proposed_value, market_value, method, control_value, income_estimate = NULL, deductions = 0, 
    deductions_not_already_included, property_type = "other", owner_occupation_suitability = NULL, rented = FALSE, 
    rental_deduction = NULL, comparable_count = NULL, qualified_model = NULL, sustainability_review = NULL)
```

Methods: income_standard, owner_cost, owner_comparison. Proposed lending value is capped by the selected method and market value after new deductions. A control value below 80 percent of the income estimate triggers a sustainability review; it is not automatically substituted as the value.

| Parameter | Meaning |
|---|---|
| `proposed_value` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `market_value` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `method` | Explicit method selector; supported choices are listed in the function-specific details. No silent fallback to an alternative regulatory method. |
| `control_value` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `income_estimate` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `deductions` | Explicit monetary deduction not already included in the input value. demolition_present_value must already be discounted. |
| `deductions_not_already_included` | Mandatory Boolean assertion that the newly supplied deductions were not already incorporated in the underlying value. |
| `property_type` | Property-method class: condominium, single_family, duplex, or other. Determines comparison-count and own-occupation checks. |
| `owner_occupation_suitability` | Boolean external assessment (or None/NULL when unresolved). An unresolved applicable assessment yields REVIEW_REQUIRED rather than automatic approval. |
| `rented` | Explicit Boolean indication that the owner-suitable property is rented and therefore needs the documented rental deduction. |
| `rental_deduction` | Explicit monetary adjustment for rental restrictions when required by the chosen property-method branch. |
| `comparable_count` | Whole number of suitably comparable objects; applicable direct-comparison branches require the documented minimum. |
| `qualified_model` | Boolean external assessment (or None/NULL when unresolved). An unresolved applicable assessment yields REVIEW_REQUIRED rather than automatic approval. |
| `sustainability_review` | Boolean external assessment (or None/NULL when unresolved). An unresolved applicable assessment yields REVIEW_REQUIRED rather than automatic approval. |

Method contract: `BEWERTUNG_ERWEITERT.md`.

Limitations: Supplied evidence flags are not authenticated; formal appraisal and value determination remain external

## foreign_perpetuity_value

Foreign perpetuity value after an explicit compensating building-depreciation cost.

```python
foreign_perpetuity_value(net_income, rate, additional_depreciation, method_evidence)
```

```r
foreign_perpetuity_value(net_income, rate, additional_depreciation, method_evidence)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `net_income` | Sustainable annual income in currency units; net_income already reflects the deductions required by the chosen method, unless explicitly used to solve an equivalent rate. |
| `rate` | Rate as a decimal, for example 0.05 for 5 percent. Its compounding and admissible bounds follow the selected method. |
| `additional_depreciation` | Explicit annual building depreciation deduction compensating for finite actual life in the foreign perpetuity convention. |
| `method_evidence` | Explicit Boolean evidence that the special foreign valuation method is applicable; the calculation does not authenticate the evidence. |

Method contract: `BEWERTUNG_ERWEITERT.md`.

Limitations: Additional depreciation must adequately compensate the actual shorter economic life

## valuation_review

Property annual-monitoring deadline and material-deterioration or arrears triggers.

```python
valuation_review(as_of, last_monitoring, material_deterioration, material_arrears_days, *, owner_occupied_residential=False)
```

```r
valuation_review(as_of, last_monitoring, material_deterioration, material_arrears_days, owner_occupied_residential = FALSE)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `as_of` | Calculation/validity date, canonical YYYY-MM-DD; R also accepts a Date scalar. Not a timestamp. |
| `last_monitoring` | Date of the last completed value monitoring; the annual deadline is obtained by adding 12 calendar months. |
| `material_deterioration` | Explicit Boolean appraisal of material deterioration in valuation fundamentals; true triggers a review. |
| `material_arrears_days` | Whole number of days of material payment arrears. The review trigger is at least 90 days, subject to the stated property exception. |
| `owner_occupied_residential` | Boolean owner-occupied residential exception to the property arrears trigger; it does not remove deterioration or annual monitoring triggers. |

Method contract: `BEWERTUNG_ERWEITERT.md`.

Limitations: Further review obligations may apply; materiality is an evidenced input

## property_parameter_check

Domestic annex life/rate controls; the official effective base rate is supplied.

```python
property_parameter_check(property_use, remaining_life, capitalization_rate, notified_base_rate, *, prime_reduction=0.0, prime_conditions=None, prime_reason=None)
```

```r
property_parameter_check(property_use, remaining_life, capitalization_rate, notified_base_rate, prime_reduction = 0, 
    prime_conditions = NULL, prime_reason = NULL)
```

Use classes and maximum lives: residential80; office/business60; department_store/shopping_center/hotel/agricultural/clinic/rehabilitation/care_home/logistics/parking/production40; leisure/specialty_market/consumer_market/petrol_station30. Supplemental capitalization rates and the eight prime conditions are checked in addition to the explicitly supplied notified base.

| Parameter | Meaning |
|---|---|
| `property_use` | Statutory property-use class; see the full allowed class/life/supplement table in the handbook. |
| `remaining_life` | Explicit duration or age in years. This is not a date or a number of days; method-specific age/life limits are checked. |
| `capitalization_rate` | Rate as a decimal, for example 0.05 for 5 percent. Its compounding and admissible bounds follow the selected method. |
| `notified_base_rate` | Explicit applicable notified capitalization base rate. The library does not fetch or silently assume a current BaFin notification. |
| `prime_reduction` | Proposed prime-property rate reduction as a decimal, at most 0.005, requiring the specified conditions and a documented reason. |
| `prime_conditions` | Mapping of the eight explicit Boolean prime conditions: urban_location, preferred_site, infrastructure, concept, equipment, construction, marketability, condition. |
| `prime_reason` | Nonempty justification for a prime-property rate reduction; required whenever a reduction is claimed. |

Method contract: `BEWERTUNG_ERWEITERT.md`.

Limitations: Official notice, effective date, market derivation and prime evidence remain externally verified inputs

## small_loan_check

§24 amount/use and inspection-exception checks; no waiver of other valuation duties.

```python
small_loan_check(loan_amount, prior_liens, commercial_income_share, domestic_residential, inspection_mode, *, years_since_inspection=None, known_object=False, comparable_object=False, prefabricated_known=False, remaining_life=None, video_complete=False, video_documented=False, valuation_haircut=0.0, essential_parameters_known=False, building_age=None, reason_documented=False)
```

```r
small_loan_check(loan_amount, prior_liens, commercial_income_share, domestic_residential, inspection_mode, years_since_inspection = NULL, 
    known_object = FALSE, comparable_object = FALSE, prefabricated_known = FALSE, remaining_life = NULL, 
    video_complete = FALSE, video_documented = FALSE, valuation_haircut = 0, essential_parameters_known = FALSE, 
    building_age = NULL, reason_documented = FALSE)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `loan_amount` | Nonnegative monetary principal or claim in the calculation currency; no implicit conversion or scaling is performed. |
| `prior_liens` | Explicit relevant prior-ranking claims in currency units. Equal-ranking slices must first be allocated consistently with the legal ranking agreement. |
| `commercial_income_share` | Fraction of sustainable income from commercial use for the small-loan test, between zero and one. |
| `domestic_residential` | Explicit Boolean confirmation of the domestic predominantly residential scope of the small-loan provision. |
| `inspection_mode` | full, known, comparable, prefabricated, video, or exterior_only. Each exception requires its documented qualifying conditions. |
| `years_since_inspection` | Explicit duration or age in years. This is not a date or a number of days; method-specific age/life limits are checked. |
| `known_object` | Explicit Boolean evidence for the selected inspection simplification; unrelated true flags do not replace its required conditions. |
| `comparable_object` | Explicit Boolean evidence for the selected inspection simplification; unrelated true flags do not replace its required conditions. |
| `prefabricated_known` | Explicit Boolean evidence for the selected inspection simplification; unrelated true flags do not replace its required conditions. |
| `remaining_life` | Explicit duration or age in years. This is not a date or a number of days; method-specific age/life limits are checked. |
| `video_complete` | Explicit Boolean evidence for the selected inspection simplification; unrelated true flags do not replace its required conditions. |
| `video_documented` | Explicit Boolean evidence for the selected inspection simplification; unrelated true flags do not replace its required conditions. |
| `valuation_haircut` | Explicit value-reduction fraction. The function applies its documented statutory minimum; a missing input is not a zero haircut. |
| `essential_parameters_known` | Explicit Boolean evidence for the selected inspection simplification; unrelated true flags do not replace its required conditions. |
| `building_age` | Explicit duration or age in years. This is not a date or a number of days; method-specific age/life limits are checked. |
| `reason_documented` | Explicit Boolean evidence for the selected inspection simplification; unrelated true flags do not replace its required conditions. |

Method contract: `BEWERTUNG_ERWEITERT.md`.

Limitations: Qualification, independence, simplified valuation, sampling and exception evidence remain required

## select_rule_profile

Choose latest known revision before checking validity; never resurrect withdrawn dates.

```python
select_rule_profile(profiles, profile_id, as_of, known_at, *, allow_experimental=False)
```

```r
select_rule_profile(profiles, profile_id, as_of, known_at, allow_experimental = FALSE)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `profiles` | Rule-profile revision records profile_id,revision,valid_from,valid_to,known_from,status,source_ref,parameters. Latest-known revision is selected before checking validity. |
| `profile_id` | Exact explicitly requested rule-profile identifier; no nearest-date or default-profile fallback. |
| `as_of` | Calculation/validity date, canonical YYYY-MM-DD; R also accepts a Date scalar. Not a timestamp. |
| `known_at` | Knowledge cutoff date, separate from the validity date. Later-known evidence and corrections are excluded. |
| `allow_experimental` | Explicit opt-in to a profile whose supplied status is EXPERIMENTAL. VERIFIED is supplied provenance, not an authenticated review. |

Method contract: `NACHWEISE_REGISTER.md`.

Limitations: Profile status is supplied provenance, not authentication of a legal review

## assess_evidence

Check supplied dated evidence; preserve missing, expired, future and failed states.

```python
assess_evidence(requirements, evidence, as_of, known_at)
```

```r
assess_evidence(requirements, evidence, as_of, known_at)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `requirements` | Nonempty requirement records requirement_id,scope,allow_not_applicable,source_ref; typically derived from position and pool inputs. |
| `evidence` | Dated evidence records evidence_id,requirement_id,scope,valid_from,valid_to,known_from,conclusion,reviewer,source_ref,reason; conclusions are MET/NOT_MET/NOT_APPLICABLE. |
| `as_of` | Calculation/validity date, canonical YYYY-MM-DD; R also accepts a Date scalar. Not a timestamp. |
| `known_at` | Knowledge cutoff date, separate from the validity date. Later-known evidence and corrections are excluded. |

Method contract: `NACHWEISE_REGISTER.md`.

Limitations: Checks presence, timing and consistency; does not authenticate evidence or prove all legal duties were included

## validate_allocations

Conserve explicit claim and qualified collateral capacities; no rank optimization.

```python
validate_allocations(claims, collateral, allocations)
```

```r
validate_allocations(claims, collateral, allocations)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `claims` | Explicit claim/collateral capacities and allocation edges. IDs, kind and currency must reconcile; the exact columns are in DATA_CONTRACTS.md. |
| `collateral` | Explicit claim/collateral capacities and allocation edges. IDs, kind and currency must reconcile; the exact columns are in DATA_CONTRACTS.md. |
| `allocations` | Explicit claim/collateral capacities and allocation edges. IDs, kind and currency must reconcile; the exact columns are in DATA_CONTRACTS.md. |

Method contract: `NACHWEISE_REGISTER.md`.

Limitations: Legal rank and qualified capacities are separately established inputs

## register_snapshot

Replay local evidenced events; never edits input history or a live legal register.

```python
register_snapshot(events, as_of, known_at)
```

```r
register_snapshot(events, as_of, known_at)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `events` | Immutable register-event records described in DATA_CONTRACTS.md. This reconstructs analytical state and does not authorize legal backdating. |
| `as_of` | Calculation/validity date, canonical YYYY-MM-DD; R also accepts a Date scalar. Not a timestamp. |
| `known_at` | Knowledge cutoff date, separate from the validity date. Later-known evidence and corrections are excluded. |

Method contract: `NACHWEISE_REGISTER.md`.

Limitations: Technical reconstruction does not establish trustee approval or legal registration

## pool_coverage

Coverage of qualified single-currency amounts with disjoint OC reservations.

```python
pool_coverage(kind, assets, liabilities, oc_allocations, *, additional_nominal=0, additional_pv=0)
```

```r
pool_coverage(kind, assets, liabilities, oc_allocations, additional_nominal = 0, additional_pv = 0)
```

Assets are already qualified amounts in one currency. OC roles reserve disjoint fractions. Nominal coverage excludes the nominal value reserved for PV OC and requires sufficient unreserved base cover; separate reserve-amount and total-PV tests remain mandatory.

| Parameter | Meaning |
|---|---|
| `kind` | Pfandbrief kind: HYP (mortgage), OEF (public sector), SCH (ship), or FLG (aircraft); transport-only methods accept SCH/FLG. |
| `assets` | Homogeneous amounts for coverage_amounts, or typed record tables for pool methods. See the per-function table contracts in DATA_CONTRACTS.md. |
| `liabilities` | Homogeneous amounts for coverage_amounts, or typed record tables for pool methods. See the per-function table contracts in DATA_CONTRACTS.md. |
| `oc_allocations` | Records asset_id, role (NOMINAL_OC/PV_OC), fraction in [0,1]; total reserved fractions per asset cannot exceed one. |
| `additional_nominal` | Explicit additional nominal or present-value cover requirement in currency units, including applicable supervisory/contractual requirements. Zero must be justified. |
| `additional_pv` | Explicit additional nominal or present-value cover requirement in currency units, including applicable supervisory/contractual requirements. Zero must be justified. |

Method contract: `POOLRECHNUNG.md`.

Limitations: Amounts must be qualified, registered and expressed in one reporting currency Checks the supplied reservations; does not optimize or authenticate qualification

## pool_limits

Statutory concentration arithmetic on explicitly classified qualified amounts.

```python
pool_limits(kind, assets, bond_nominal, bond_pv, derivative_liabilities)
```

```r
pool_limits(kind, assets, bond_nominal, bond_pv, derivative_liabilities)
```

T1/T2/T3/T4 limits are cumulative 8/10/15/20 percent, with no generic T4 limit for OEF. Pure-liquidity and PV-OC exemptions have distinct scopes. The bank-group limit is not automatically waived for PV OC. All classifications require evidence.

| Parameter | Meaning |
|---|---|
| `kind` | Pfandbrief kind: HYP (mortgage), OEF (public sector), SCH (ship), or FLG (aircraft); transport-only methods accept SCH/FLG. |
| `assets` | Homogeneous amounts for coverage_amounts, or typed record tables for pool methods. See the per-function table contracts in DATA_CONTRACTS.md. |
| `bond_nominal` | Aggregate qualified nominal or present value, in one currency. Bond denominators exclude derivative liabilities unless the method explicitly adds them. |
| `bond_pv` | Aggregate qualified nominal or present value, in one currency. Bond denominators exclude derivative liabilities unless the method explicitly adds them. |
| `derivative_liabilities` | Records liability_id, kind, present_value, pure_fx_hedge. Negative derivative values remain covered even when evidence is incomplete. |

Method contract: `POOLRECHNUNG.md`.

Limitations: Classification, exemptions, foreign priority and any special permissions require separate evidence No generic exemption from the bank-group limit for PV OC assets

## pool_stress

Net stressed values by currency, then apply adverse FX; three scenarios required.

```python
pool_stress(kind, valuations, fx_rates)
```

```r
pool_stress(kind, valuations, fx_rates)
```

Input is one signed valuation per position and BASE/UP/DOWN scenario. UP/DOWN are currency-netted before adverse FX. The highest deficit is relative to base coverage, without adding a new 2-percent OC requirement inside every stress.

| Parameter | Meaning |
|---|---|
| `kind` | Pfandbrief kind: HYP (mortgage), OEF (public sector), SCH (ship), or FLG (aircraft); transport-only methods accept SCH/FLG. |
| `valuations` | Records position_id, kind, currency, scenario (BASE/UP/DOWN), signed_present_value; every position must occur in all three scenarios. |
| `fx_rates` | Records currency, eur_per_unit, shock. EUR requires 1 and 0. Every position currency must have an explicit row. |

Method contract: `POOLRECHNUNG.md`.

Limitations: Each scenario must contain independently qualified valuations and all derivative liabilities Separate base PV OC requirement is checked by pool_coverage

## liquidity_180

Exactly 180 following calendar days; no assumed maturity extension or reinvestment.

```python
liquidity_180(as_of, cashflows, buffers)
```

```r
liquidity_180(as_of, cashflows, buffers)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `as_of` | Calculation/validity date, canonical YYYY-MM-DD; R also accepts a Date scalar. Not a timestamp. |
| `cashflows` | Records flow_id, position_id, date, inflow, outflow. All days are retained by the 180-day ledger; dates after the horizon do not affect its maximum deficit. |
| `buffers` | Records asset_id, qualified_value, monetized, qualification_ref. Monetized asset inflows are removed; payment obligations remain. |

Method contract: `POOLRECHNUNG.md`.

Limitations: Buffer qualification and amounts must be supplied separately in the cashflow reporting currency Monetized assets lose their contractual inflows; payments owed remain included

## cover_amount

Nominal upper bound after rank, redemption and explicit default treatment.

```python
cover_amount(category, claim, registered, redemption, *, defaulted, guaranteed, guarantor_defaulted, lien=None, lending_value=None, prior_claims=None, guarantee_amount=None, lending_limit=0.6)
```

```r
cover_amount(category, claim, registered, redemption, defaulted, guaranteed, guarantor_defaulted, lien = NULL, 
    lending_value = NULL, prior_claims = NULL, guarantee_amount = NULL, lending_limit = 0.6)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `category` | Explicit instrument or liquidity category accepted by the function; classification is never guessed from a free-text security name. |
| `claim` | Nonnegative monetary principal or claim in the calculation currency; no implicit conversion or scaling is performed. |
| `registered` | Explicit amount assigned to this cover register/tranche, in the same currency as the claim. |
| `redemption` | Explicit lower permissible asset redemption amount; enter the claim amount when no lower redemption is possible. |
| `defaulted` | Explicit Boolean default or qualifying-guarantee fact. Missing evidence must not be replaced with false. |
| `guaranteed` | Explicit Boolean default or qualifying-guarantee fact. Missing evidence must not be replaced with false. |
| `guarantor_defaulted` | Explicit Boolean default or qualifying-guarantee fact. Missing evidence must not be replaced with false. |
| `lien` | Amount of the institution's own legally effective collateral right, excluding separately specified prior claims. |
| `lending_value` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `prior_claims` | Explicit relevant prior-ranking claims in currency units. Equal-ranking slices must first be allocated consistently with the legal ranking agreement. |
| `guarantee_amount` | Amount actually covered by the qualifying guarantee, required only when guaranteed is true. |
| `lending_limit` | Eligible first-rank fraction of lending value, expressed as a decimal. Any departure from the regular 0.60 requires an applicable evidenced rule or exception. |

Method contract: `EIGNUNG_INTEGRATION.md`.

Limitations: External eligibility, prior/equal rank allocation and the value appraisal remain prerequisites Any lending-limit departure from .60 requires an applicable evidenced exception/profile

## mortgage_terms_check

Permitted location group and fixed-term-right calendar boundaries.

```python
mortgage_terms_check(country_group, maturity, *, permanent_income, construction_or_land, right_expiry=None, economic_end=None)
```

```r
mortgage_terms_check(country_group, maturity, permanent_income, construction_or_land, right_expiry = NULL, economic_end = NULL)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `country_group` | EU_EEA, CH, GB, US, CA, JP, AU, NZ, SG, or OTHER for the mortgage-location test; group membership itself requires evidence. |
| `maturity` | Explicit calendar date in YYYY-MM-DD (or an R Date). The argument name identifies the contractual boundary; intervals must be chronological. |
| `permanent_income` | Explicit Boolean permanent-income or permitted construction/building-land facts used in the property eligibility check. |
| `construction_or_land` | Explicit Boolean permanent-income or permitted construction/building-land facts used in the property eligibility check. |
| `right_expiry` | Explicit calendar date in YYYY-MM-DD (or an R Date). The argument name identifies the contractual boundary; intervals must be chronological. |
| `economic_end` | Explicit calendar date in YYYY-MM-DD (or an R Date). The argument name identifies the contractual boundary; intervals must be chronological. |

Method contract: `EIGNUNG_INTEGRATION.md`.

Limitations: Country membership, comparable legal rights and lasting income require evidence

## transport_loan_check

Annual amortization, permitted balloon, life and deferral checks for SCH/FLG.

```python
transport_loan_check(kind, loan_amount, annual_amortizations, balloon, age_at_maturity, expected_life, defer_years, *, maturity_exception=False, repayment_exception=False, defer_exception=False, extended_forbearance=False, trustee_consent=False, reconciliation_tolerance=1e-08)
```

```r
transport_loan_check(kind, loan_amount, annual_amortizations, balloon, age_at_maturity, expected_life, defer_years, 
    maturity_exception = FALSE, repayment_exception = FALSE, defer_exception = FALSE, extended_forbearance = FALSE, 
    trustee_consent = FALSE, reconciliation_tolerance = 1e-08)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `kind` | Pfandbrief kind: HYP (mortgage), OEF (public sector), SCH (ship), or FLG (aircraft); transport-only methods accept SCH/FLG. |
| `loan_amount` | Nonnegative monetary principal or claim in the calculation currency; no implicit conversion or scaling is performed. |
| `annual_amortizations` | Annual regular principal repayments excluding the final balloon; nonempty, nonnegative and reconciled to the original loan plus balloon. |
| `balloon` | Final additional repayment in currency units, tested against the statutory regular-amortization capacity. |
| `age_at_maturity` | Explicit duration or age in years. This is not a date or a number of days; method-specific age/life limits are checked. |
| `expected_life` | Explicit duration or age in years. This is not a date or a number of days; method-specific age/life limits are checked. |
| `defer_years` | Explicit duration or age in years. This is not a date or a number of days; method-specific age/life limits are checked. |
| `maturity_exception` | Explicit assertion that an individual statutory exception has been granted. The returned required_approval_evidence must be assessed separately. |
| `repayment_exception` | Explicit assertion that an individual statutory exception has been granted. The returned required_approval_evidence must be assessed separately. |
| `defer_exception` | Explicit assertion that an individual statutory exception has been granted. The returned required_approval_evidence must be assessed separately. |
| `extended_forbearance` | Explicit facts about forbearance beyond the normal term and the corresponding trustee consent; missing consent is not inferred. |
| `trustee_consent` | Explicit facts about forbearance beyond the normal term and the corresponding trustee consent; missing consent is not inferred. |
| `reconciliation_tolerance` | Explicit numerical reconciliation tolerance. It is not applied to statutory limit or eligibility boundary decisions. |

Method contract: `EIGNUNG_INTEGRATION.md`.

Limitations: Annual repayments exclude the final balloon; exceptions and consent need separate dated evidence

## insurance_check

Amount test only; rights, insured risks and notices remain separate evidence.

```python
insurance_check(kind, insured_amount, claim, *, prior_equal_claims=0, basis=None, reconstruction_cost=None, probable_maximum_loss=None, current_value_loss=None)
```

```r
insurance_check(kind, insured_amount, claim, prior_equal_claims = 0, basis = NULL, reconstruction_cost = NULL, 
    probable_maximum_loss = NULL, current_value_loss = NULL)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `kind` | Pfandbrief kind: HYP (mortgage), OEF (public sector), SCH (ship), or FLG (aircraft); transport-only methods accept SCH/FLG. |
| `insured_amount` | Actual available insurance amount under the selected permissible insurance basis, in the same currency as the claim. |
| `claim` | Nonnegative monetary principal or claim in the calculation currency; no implicit conversion or scaling is performed. |
| `prior_equal_claims` | Prior- or equal-ranking third-party ship/aircraft rights to be added after calculating 110 percent of the own outstanding loan. |
| `basis` | HYP insurance basis: reconstruction, probable_maximum_loss, or claim_current_value. SCH/FLG instead use claim and third-party rights. |
| `reconstruction_cost` | Nonnegative amount for the selected property-insurance basis; supply only that basis, not contradictory unused amounts. |
| `probable_maximum_loss` | Nonnegative amount for the selected property-insurance basis; supply only that basis, not contradictory unused amounts. |
| `current_value_loss` | Nonnegative amount for the selected property-insurance basis; supply only that basis, not contradictory unused amounts. |

Method contract: `EIGNUNG_INTEGRATION.md`.

Limitations: Transport formula: 110% of own outstanding claim plus prior/equal third-party rights Does not establish insured risks, legal entitlement, notices or annual loss-cap validity

## required_evidence

Derive a nonempty evidence contract from position category and explicit features.

```python
required_evidence(kind, position_id, category, features=())
```

```r
required_evidence(kind, position_id, category, features = character())
```

Categories: MORTGAGE,PUBLIC,SHIP,AIRCRAFT,SUBSTITUTE,DERIVATIVE,BOND. Features: foreign,partial,refinancing,guaranteed,pv_oc,liquidity,legacy,exception,own_held,payment_settlement. Legal evidence is assessed, not authenticated.

| Parameter | Meaning |
|---|---|
| `kind` | Pfandbrief kind: HYP (mortgage), OEF (public sector), SCH (ship), or FLG (aircraft); transport-only methods accept SCH/FLG. |
| `position_id` | Stable nonempty position/scope identifier, unique within the relevant input table. |
| `category` | Explicit instrument or liquidity category accepted by the function; classification is never guessed from a free-text security name. |
| `features` | Explicit list of applicable evidence/register features; optional conditions cannot be hidden by omitting a feature that is actually present. |

Method contract: `EIGNUNG_INTEGRATION.md`.

Limitations: Requires truthful position classification; presence of evidence does not authenticate its conclusion

## pool_requirements

Derive all mandatory position and pool evidence before an integrated run.

```python
pool_requirements(kind, positions, oc_allocations, buffers)
```

```r
pool_requirements(kind, positions, oc_allocations, buffers)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `kind` | Pfandbrief kind: HYP (mortgage), OEF (public sector), SCH (ship), or FLG (aircraft); transport-only methods accept SCH/FLG. |
| `positions` | Function-specific position records. Integrated pools require the complete common universe; metrics require their documented fields. See DATA_CONTRACTS.md. |
| `oc_allocations` | Records asset_id, role (NOMINAL_OC/PV_OC), fraction in [0,1]; total reserved fractions per asset cannot exceed one. |
| `buffers` | Records asset_id, qualified_value, monetized, qualification_ref. Monetized asset inflows are removed; payment obligations remain. |

Method contract: `POOL_DATENVERTRAG.md`.

## analyze_pool

Integrate explicit valuations, coverage, limits, liquidity and dated evidence in EUR.

```python
analyze_pool(kind, positions, oc_allocations, cashflows, buffers, fx_rates, evidence, as_of, known_at, *, additional_nominal=0, additional_pv=0)
```

```r
analyze_pool(kind, positions, oc_allocations, cashflows, buffers, fx_rates, evidence, as_of, known_at, additional_nominal = 0, 
    additional_pv = 0)
```

One complete position universe drives coverage, limits, stress and 180-day liquidity in EUR. Required evidence is derived by pool_requirements. Missing evidence leaves hypothetical calculations visible with INCOMPLETE; negative evidence excludes positive assets but never removes negative derivative liabilities. Input record schemas are essential: see DATA_CONTRACTS.md.

| Parameter | Meaning |
|---|---|
| `kind` | Pfandbrief kind: HYP (mortgage), OEF (public sector), SCH (ship), or FLG (aircraft); transport-only methods accept SCH/FLG. |
| `positions` | Function-specific position records. Integrated pools require the complete common universe; metrics require their documented fields. See DATA_CONTRACTS.md. |
| `oc_allocations` | Records asset_id, role (NOMINAL_OC/PV_OC), fraction in [0,1]; total reserved fractions per asset cannot exceed one. |
| `cashflows` | Records flow_id, position_id, date, inflow, outflow. All days are retained by the 180-day ledger; dates after the horizon do not affect its maximum deficit. |
| `buffers` | Records asset_id, qualified_value, monetized, qualification_ref. Monetized asset inflows are removed; payment obligations remain. |
| `fx_rates` | Records currency, eur_per_unit, shock. EUR requires 1 and 0. Every position currency must have an explicit row. |
| `evidence` | Dated evidence records evidence_id,requirement_id,scope,valid_from,valid_to,known_from,conclusion,reviewer,source_ref,reason; conclusions are MET/NOT_MET/NOT_APPLICABLE. |
| `as_of` | Calculation/validity date, canonical YYYY-MM-DD; R also accepts a Date scalar. Not a timestamp. |
| `known_at` | Knowledge cutoff date, separate from the validity date. Later-known evidence and corrections are excluded. |
| `additional_nominal` | Explicit additional nominal or present-value cover requirement in currency units, including applicable supervisory/contractual requirements. Zero must be justified. |
| `additional_pv` | Explicit additional nominal or present-value cover requirement in currency units, including applicable supervisory/contractual requirements. Zero must be justified. |

Method contract: `POOL_DATENVERTRAG.md`.

Limitations: CHECKS_PASSED covers implemented calculations and supplied evidence consistency, not authenticity or supervisory approval PV inputs must already value the qualified tranche; derivatives are independent framework market values Open evidence makes the otherwise calculated amounts hypothetical

```python
result = analyze_pool(**cashflow_example_pool("HYP").value)
result.value
```

## example_pool

Build a synthetic EUR par-value pool and explicitly fictional evidence.

```python
example_pool(kind, *, scale=1000000)
```

```r
example_pool(kind, scale = 1e+06)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `kind` | Pfandbrief kind: HYP (mortgage), OEF (public sector), SCH (ship), or FLG (aircraft); transport-only methods accept SCH/FLG. |
| `scale` | Positive currency multiplier for synthetic examples. Default one million; 1 produces small independently checkable amounts. |

Method contract: `POOL_DATENVERTRAG.md`.

Limitations: All evidence and scenario values are fictional; never reuse as actual regulatory evidence No cashflows within 180 days assumed; this example illustrates integration, not realistic interest-rate dynamics

```python
example_pool("SCH", scale=1)
```

## cashflow_example_pool

Synthetic cashflow-to-pool example with genuine repricing and a coupon liquidity gap.

```python
cashflow_example_pool(kind, *, scale=1000000)
```

```r
cashflow_example_pool(kind, scale = 1e+06)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `kind` | Pfandbrief kind: HYP (mortgage), OEF (public sector), SCH (ship), or FLG (aircraft); transport-only methods accept SCH/FLG. |
| `scale` | Positive currency multiplier for synthetic examples. Default one million; 1 produces small independently checkable amounts. |

Method contract: `POOL_DATENVERTRAG.md`.

Limitations: All legal evidence is fictional; supplied scenario prices are now computed from disclosed cashflows Illustrative annual asset coupons and quarterly bond coupons; no customer data or actual market quotation

```python
data = cashflow_example_pool("FLG")
analyze_pool(**data.value).value
```

## covered_bond_risk_weight

CRR Art129 mapping, conditional on separately established full eligibility.

```python
covered_bond_risk_weight(*, eligibility_status, cqs=None, issuer_risk_weight=None)
```

```r
covered_bond_risk_weight(eligibility_status, cqs = NULL, issuer_risk_weight = NULL)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `eligibility_status` | Explicit external assessment: MET, NOT_MET or MISSING. The function preserves missing/negative evidence rather than inventing approval. |
| `cqs` | Directly applicable whole-number credit quality step. The permitted range depends on the mapping or exposure test. |
| `issuer_risk_weight` | Explicit decimal risk weight for the unrated route, used only when no directly applicable CQS is supplied. |

Method contract: `EU_LIQUIDITAET.md`.

Limitations: No calculation of the issuer risk weight or determination of overall CRR eligibility

```python
covered_bond_risk_weight(eligibility_status="MET", cqs=2)
```

## european_label

German PfandBG §41a label conditions, separate from investor risk weights.

```python
european_label(kind, issue_date, *, pfandbrief_status)
```

```r
european_label(kind, issue_date, pfandbrief_status)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `kind` | Pfandbrief kind: HYP (mortgage), OEF (public sector), SCH (ship), or FLG (aircraft); transport-only methods accept SCH/FLG. |
| `issue_date` | Original issue date used for the explicitly described label or CRR transition rules. |
| `pfandbrief_status` | Explicit external assessment: MET, NOT_MET or MISSING. The function preserves missing/negative evidence rather than inventing approval. |

Method contract: `EU_LIQUIDITAET.md`.

Limitations: Applies to German Pfandbriefe; qualifying foreign instruments require their own supervisory evidence

## crr_pool_check

Numerical Art129 OC and bank limits for one homogeneous issue-date cohort.

```python
crr_pool_check(assets_nominal, bonds_nominal, bank_exposures, issue_date, as_of, *, eligibility_status, required_oc=0.05, national_reduction_status='MISSING', legacy_status='MISSING')
```

```r
crr_pool_check(assets_nominal, bonds_nominal, bank_exposures, issue_date, as_of, eligibility_status, required_oc = 0.05, 
    national_reduction_status = "MISSING", legacy_status = "MISSING")
```

Only one homogeneous issue-date cohort per call. Documented pre-2007 and pre-2022 cohorts have different Article129 exemptions. Eligible collateral, per-loan caps, valuation and legal qualification must be independently assessed; a numerical limit pass alone does not establish Article129 eligibility.

| Parameter | Meaning |
|---|---|
| `assets_nominal` | Aggregate qualified nominal or present value, in one currency. Bond denominators exclude derivative liabilities unless the method explicitly adds them. |
| `bonds_nominal` | Aggregate qualified nominal or present value, in one currency. Bond denominators exclude derivative liabilities unless the method explicitly adds them. |
| `bank_exposures` | Art129 bank records exposure_id,amount,cqs,oc_amount,settlement_amount,category,original_days,approved; OC and settlement exemptions must not overlap beyond the amount. |
| `issue_date` | Original issue date used for the explicitly described label or CRR transition rules. |
| `as_of` | Calculation/validity date, canonical YYYY-MM-DD; R also accepts a Date scalar. Not a timestamp. |
| `eligibility_status` | Explicit external assessment: MET, NOT_MET or MISSING. The function preserves missing/negative evidence rather than inventing approval. |
| `required_oc` | Required or observed overcollateralization fraction above liabilities, for example 0.02 for 2 percent. Not the asset/liability ratio 1.02. |
| `national_reduction_status` | Explicit external assessment: MET, NOT_MET or MISSING. The function preserves missing/negative evidence rather than inventing approval. |
| `legacy_status` | Explicit external assessment: MET, NOT_MET or MISSING. The function preserves missing/negative evidence rather than inventing approval. |

Method contract: `EU_LIQUIDITAET.md`.

Limitations: Requires separately evidenced eligible collateral, per-loan limits, Art208/229 valuation and legal qualifications Issue-date cohorts must be homogeneous; this is not a general RWA calculation

## covered_bond_lcr

LCR covered-bond category candidates; unknown conditions remain visible.

```python
covered_bond_lcr(issue_size_eur, overcollateralization, conditions, *, cqs=None, unrated_risk_weight=None, regime='EU')
```

```r
covered_bond_lcr(issue_size_eur, overcollateralization, conditions, cqs = NULL, unrated_risk_weight = NULL, 
    regime = "EU")
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `issue_size_eur` | Issue amount expressed in EUR, not millions of EUR, for the LCR issuance-size thresholds. |
| `overcollateralization` | Required or observed overcollateralization fraction above liabilities, for example 0.02 for 2 percent. Not the asset/liability ratio 1.02. |
| `conditions` | LCR condition mapping with Boolean values or None/NULL for unresolved conditions; candidate-specific required keys are retained in the result. |
| `cqs` | Directly applicable whole-number credit quality step. The permitted range depends on the mapping or exposure test. |
| `unrated_risk_weight` | Explicit decimal risk weight for the unrated route, used only when no directly applicable CQS is supplied. |
| `regime` | EU or THIRD_COUNTRY covered-bond LCR route; distinct legal and supervision conditions apply. |

Method contract: `EU_LIQUIDITAET.md`.

Limitations: Conditions are external legal/portfolio assessments; general operational liquidity requirements remain separately evidenced Uses the explicit locally archived LCR edition; no automatic future-rule substitution

## liquid_buffer_value

Art9 market-value haircut or <=3-calendar-month qualified bank deposit.

```python
liquid_buffer_value(market_value, category, *, qualification_status, haircut=None, additional_fx_haircut=0, as_of=None, maturity=None)
```

```r
liquid_buffer_value(market_value, category, qualification_status, haircut = NULL, additional_fx_haircut = 0, as_of = NULL, 
    maturity = NULL)
```

Categories: LEVEL1_OTHER,LEVEL1_COVERED,LEVEL2A,LEVEL2B_COVERED,LEVEL2B_OTHER,LEVEL2B_SECURITIZATION,RESTRICTED_FACILITY,BANK_DEPOSIT. Minimum haircuts are 0,.07,.15,.30,.50 for the first five. The last two specialized LCR categories need an explicit haircut. BANK_DEPOSIT needs as_of and maturity within three calendar months.

| Parameter | Meaning |
|---|---|
| `market_value` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `category` | Explicit instrument or liquidity category accepted by the function; classification is never guessed from a free-text security name. |
| `qualification_status` | Explicit external assessment: MET, NOT_MET or MISSING. The function preserves missing/negative evidence rather than inventing approval. |
| `haircut` | Explicit value-reduction fraction. The function applies its documented statutory minimum; a missing input is not a zero haircut. |
| `additional_fx_haircut` | Additional explicit FX haircut applied to the value remaining after the asset-class liquidity haircut. |
| `as_of` | Calculation/validity date, canonical YYYY-MM-DD; R also accepts a Date scalar. Not a timestamp. |
| `maturity` | Explicit calendar date in YYYY-MM-DD (or an R Date). The argument name identifies the contractual boundary; intervals must be chronological. |

Method contract: `EU_LIQUIDITAET.md`.

Limitations: Qualification includes asset-specific and general requirements; it is not established by the haircut calculation No total LCR composition caps are imposed on the Pfandbrief liquidity buffer

```python
liquid_buffer_value(100, "LEVEL1_COVERED", qualification_status="MET")
```

## validate_register_entries

Check proposed admissions and fields; never writes a legal cover register.

```python
validate_register_entries(entries, used_numbers)
```

```r
validate_register_entries(entries, used_numbers)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `entries` | Proposed register-admission records or the complete inventory of previously used register numbers, including deleted entries. See the register data contract. |
| `used_numbers` | Proposed register-admission records or the complete inventory of previously used register numbers, including deleted entries. See the register data contract. |

Method contract: `REGISTER_ABWICKLUNG.md`.

Limitations: Input features must fully describe applicable rights and arrangements; legal contents are not authenticated used_numbers must include previously deleted entries; this is a proposed-admission check, not a historical correction model

## deferred_interest

Simple contractual accrual on a deferred amount, including capitalized overdue interest.

```python
deferred_interest(amount, coupon_rate, original_date, new_date, day_count)
```

```r
deferred_interest(amount, coupon_rate, original_date, new_date, day_count)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `amount` | Nonnegative monetary principal or claim in the calculation currency; no implicit conversion or scaling is performed. |
| `coupon_rate` | Rate as a decimal, for example 0.05 for 5 percent. Its compounding and admissible bounds follow the selected method. |
| `original_date` | Explicit calendar date in YYYY-MM-DD (or an R Date). The argument name identifies the contractual boundary; intervals must be chronological. |
| `new_date` | Explicit calendar date in YYYY-MM-DD (or an R Date). The argument name identifies the contractual boundary; intervals must be chronological. |
| `day_count` | ACT/365F, ACT/360, 30E/360 (European, not ISDA-February), or ACT/ACT-ISDA. Fractions are unrounded. |

Method contract: `REGISTER_ABWICKLUNG.md`.

Limitations: Applies the supplied existing coupon and convention; differing contractual agreements require explicit inputs

## interest_extension

First-month interest deferral to the end of the month following appointment.

```python
interest_extension(amount, coupon_rate, original_date, appointment_date, decision_date, day_count, *, authority_status)
```

```r
interest_extension(amount, coupon_rate, original_date, appointment_date, decision_date, day_count, authority_status)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `amount` | Nonnegative monetary principal or claim in the calculation currency; no implicit conversion or scaling is performed. |
| `coupon_rate` | Rate as a decimal, for example 0.05 for 5 percent. Its compounding and admissible bounds follow the selected method. |
| `original_date` | Explicit calendar date in YYYY-MM-DD (or an R Date). The argument name identifies the contractual boundary; intervals must be chronological. |
| `appointment_date` | Evidenced administrator appointment or decision date, YYYY-MM-DD. A decision cannot precede the appointment. |
| `decision_date` | Evidenced administrator appointment or decision date, YYYY-MM-DD. A decision cannot precede the appointment. |
| `day_count` | ACT/365F, ACT/360, 30E/360 (European, not ISDA-February), or ACT/ACT-ISDA. Fractions are unrounded. |
| `authority_status` | Explicit external assessment: MET, NOT_MET or MISSING. The function preserves missing/negative evidence rather than inventing approval. |

Method contract: `REGISTER_ABWICKLUNG.md`.

Limitations: Requires evidenced administrator authority and separate reconciliation of all affected emissions

## extension_plan

Check an issue-uniform principal deferral scenario and repayment order.

```python
extension_plan(kind, issues, appointment_date, decision_date, *, authority_status, conditions_status, complete_scope_status)
```

```r
extension_plan(kind, issues, appointment_date, decision_date, authority_status, conditions_status, complete_scope_status)
```

Principal-only scenario with two possible payment dates per issue: unshifted share and deferred share. Maximum shift is 12 calendar months. At each planned payment date, later-originally-due issues cannot have a higher repayment fraction than an earlier still-outstanding issue. This leaves base contractual cashflows unchanged.

| Parameter | Meaning |
|---|---|
| `kind` | Pfandbrief kind: HYP (mortgage), OEF (public sector), SCH (ship), or FLG (aircraft); transport-only methods accept SCH/FLG. |
| `issues` | One principal-deferral record per issue: issue_id,kind,original_date,new_date,principal,shifted_fraction,coupon_rate,day_count. |
| `appointment_date` | Evidenced administrator appointment or decision date, YYYY-MM-DD. A decision cannot precede the appointment. |
| `decision_date` | Evidenced administrator appointment or decision date, YYYY-MM-DD. A decision cannot precede the appointment. |
| `authority_status` | Explicit external assessment: MET, NOT_MET or MISSING. The function preserves missing/negative evidence rather than inventing approval. |
| `conditions_status` | Explicit external assessment: MET, NOT_MET or MISSING. The function preserves missing/negative evidence rather than inventing approval. |
| `complete_scope_status` | Explicit external assessment: MET, NOT_MET or MISSING. The function preserves missing/negative evidence rather than inventing approval. |

Method contract: `REGISTER_ABWICKLUNG.md`.

Limitations: Explicit principal-only two-payment scenario per issue; no automatic modification of base cashflows Complete scope evidence must cover all affected issues, interest-payment interactions and contractual departures Derivatives and new administrator liabilities are outside the statutory deferral power

## pool_metrics

Extract reconciled metrics from one analyze_pool result, retaining its decision.

```python
pool_metrics(result)
```

```r
pool_metrics(result)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `result` | A native result returned specifically by analyze_pool, retaining coverage, limits, stress, liquidity, evidence and atomic positions. |

Method contract: `KENNZAHLEN.md`.

Limitations: No complete statutory disclosure or supervisory filing; stress is reported as a net balance

```python
pool_metrics(analyze_pool(**example_pool("OEF").value))
```

## aggregate_positions

Explicit amount aggregation over unique positions; grouping fields must be strings.

```python
aggregate_positions(positions, group_fields, value_field)
```

```r
aggregate_positions(positions, group_fields, value_field)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `positions` | Function-specific position records. Integrated pools require the complete common universe; metrics require their documented fields. See DATA_CONTRACTS.md. |
| `group_fields` | Explicit grouping-column names or numeric amount-column name; every grouping value must be nonempty text and position IDs must be unique. |
| `value_field` | Explicit grouping-column names or numeric amount-column name; every grouping value must be nonempty text and position IDs must be unique. |

Method contract: `KENNZAHLEN.md`.

Limitations: Caller must group by kind and currency wherever amounts are not homogeneous

## maturity_buckets

Calendar-month bands for explicitly supplied maturity or repricing dates.

```python
maturity_buckets(positions, as_of)
```

```r
maturity_buckets(positions, as_of)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `positions` | Function-specific position records. Integrated pools require the complete common universe; metrics require their documented fields. See DATA_CONTRACTS.md. |
| `as_of` | Calculation/validity date, canonical YYYY-MM-DD; R also accepts a Date scalar. Not a timestamp. |

Method contract: `KENNZAHLEN.md`.

Limitations: Use bond maturity for liabilities and contractual repricing date for cover assets

## weighted_ltv

§28(2)3 LTV: used lien plus prior/equal liens; highest used lien per property.

```python
weighted_ltv(positions)
```

```r
weighted_ltv(positions)
```

Fields: position_id,property_id,allocated_amount,used_lien_with_prior_equal,lending_value. Only the highest used-lien LTV for each property contributes, with that claim's weight. Equal maxima require explicit consolidation. Do not substitute the full borrower-loan LTV.

| Parameter | Meaning |
|---|---|
| `positions` | Function-specific position records. Integrated pools require the complete common universe; metrics require their documented fields. See DATA_CONTRACTS.md. |

Method contract: `KENNZAHLEN.md`.

Limitations: Uses the cover-used lien, not the full borrower loan; prior and equal third-party liens must already be included Same-property liens retain only the highest LTV and that claim's weight; equal maxima require consolidation

## reconcile_totals

Numerical reconciliation tolerance; never changes a statutory limit decision.

```python
reconcile_totals(actual, expected, *, absolute_tolerance=1e-08, relative_tolerance=1e-12)
```

```r
reconcile_totals(actual, expected, absolute_tolerance = 1e-08, relative_tolerance = 1e-12)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `actual` | Named numeric mappings for reconciliation. Absent/None/NULL values produce INCOMPLETE rather than a zero comparison. |
| `expected` | Named numeric mappings for reconciliation. Absent/None/NULL values produce INCOMPLETE rather than a zero comparison. |
| `absolute_tolerance` | Explicit numerical reconciliation tolerance. It is not applied to statutory limit or eligibility boundary decisions. |
| `relative_tolerance` | Explicit numerical reconciliation tolerance. It is not applied to statutory limit or eligibility boundary decisions. |

Method contract: `KENNZAHLEN.md`.

## export_table

Write flat scalar records to an explicit CSV path; no package-resource writes.

```python
export_table(rows, path, *, overwrite=False)
```

```r
export_table(rows, path, overwrite = FALSE)
```

UTF-8 CSV, comma delimiter, quoted cells, decimal point and 17 significant numeric digits. Missing values become empty fields. For lossless nested native results use Python JSON from as_dict or R saveRDS. No official regulatory filing format is produced.

| Parameter | Meaning |
|---|---|
| `rows` | Nonempty homogeneous flat records for CSV export; values are strings, finite numeric scalars, Booleans or missing values. |
| `path` | Explicit local output filename. Its parent directory must exist; installed package resources are read-only export targets. |
| `overwrite` | Explicit Boolean permission to replace an existing output file. Default false protects an existing file. |

Method contract: `KENNZAHLEN.md`.

## cashflow_scenarios

Three valuations of fixed linear cashflows; FX is a separate currency-net step.

```python
cashflow_scenarios(amounts, times, curve_times, zero_rates, *, method, history=None, ddof=1, extrapolation='error', spread=0)
```

```r
cashflow_scenarios(amounts, times, curve_times, zero_rates, method, history = NULL, ddof = 1, extrapolation = "error", 
    spread = 0)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `amounts` | Explicit cashflow amounts in one currency, matching times. Signed cashflows are accepted by PV methods; bond yield analytics require nonnegative future payments. |
| `times` | Explicit year coordinates relative to the valuation date. Curve nodes must be strictly increasing; floating-coupon starts/ends/resets follow the documented in-advance convention. |
| `curve_times` | Explicit year coordinates relative to the valuation date. Curve nodes must be strictly increasing; floating-coupon starts/ends/resets follow the documented in-advance convention. |
| `zero_rates` | Continuously compounded decimal zero rates at the supplied curve nodes. Rates may be negative; no implicit zero floor is imposed. |
| `method` | Explicit method selector; supported choices are listed in the function-specific details. No silent fallback to an alternative regulatory method. |
| `history` | For dynamic stress: exactly 250 observations. Rate history is a row-by-tenor table; FX history is a positive numeric vector. |
| `ddof` | Standard-deviation divisor correction, 0 or 1; the default 1 uses the sample divisor. This explicit statistical convention is retained in output. |
| `extrapolation` | error rejects cashflows outside the curve; flat_zero explicitly extends the endpoint zero rates. |
| `spread` | Explicit decimal spread. spread shifts the continuous discount curve; margin is added to the floating index coupon. |

Method contract: `ANALYTIK_ERGAENZUNGEN.md`.

Limitations: Fixed amounts are not reprojected under stress; floating coupons must be reprojected separately Not an embedded-option model or independent derivative market price

```python
cashflow_scenarios([100], [1], [0, 2], [0, 0], method="static")
```

## project_floating_coupons

In-advance simple forward coupons with explicit historical fixings and bound basis.

```python
project_floating_coupons(reset_times, start_times, end_times, accrual_fractions, fixings, curve_times, zero_rates, *, margin=0, floor=None, cap=None, bound_on='all_in', extrapolation='error')
```

```r
project_floating_coupons(reset_times, start_times, end_times, accrual_fractions, fixings, curve_times, zero_rates, margin = 0, 
    floor = NULL, cap = NULL, bound_on = "all_in", extrapolation = "error")
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `reset_times` | Explicit year coordinates relative to the valuation date. Curve nodes must be strictly increasing; floating-coupon starts/ends/resets follow the documented in-advance convention. |
| `start_times` | Explicit year coordinates relative to the valuation date. Curve nodes must be strictly increasing; floating-coupon starts/ends/resets follow the documented in-advance convention. |
| `end_times` | Explicit year coordinates relative to the valuation date. Curve nodes must be strictly increasing; floating-coupon starts/ends/resets follow the documented in-advance convention. |
| `accrual_fractions` | Positive contractual coupon year fractions, separately supplied from the projection curve time coordinates. |
| `fixings` | One actual index fixing per past/current reset and None/NULL per future reset. R uses a list to retain missing elements; no NA fallback. |
| `curve_times` | Explicit year coordinates relative to the valuation date. Curve nodes must be strictly increasing; floating-coupon starts/ends/resets follow the documented in-advance convention. |
| `zero_rates` | Continuously compounded decimal zero rates at the supplied curve nodes. Rates may be negative; no implicit zero floor is imposed. |
| `margin` | Explicit decimal spread. spread shifts the continuous discount curve; margin is added to the floating index coupon. |
| `floor` | Optional decimal coupon/index bounds, explicitly distinguished by bound_on. No implied option price is calculated. |
| `cap` | Optional decimal coupon/index bounds, explicitly distinguished by bound_on. No implied option price is calculated. |
| `bound_on` | index applies bounds before adding margin; all_in applies bounds to index plus margin. |
| `extrapolation` | error rejects cashflows outside the curve; flat_zero explicitly extends the endpoint zero rates. |

Method contract: `ANALYTIK_ERGAENZUNGEN.md`.

Limitations: Projection curve and coupon day fractions are explicit inputs; no option time value or in-arrears convexity model

## effective_sensitivities

Parallel continuous-zero-rate finite differences; separate from statutory stress.

```python
effective_sensitivities(amounts, times, curve_times, zero_rates, *, bump=0.0001, spread=0, extrapolation='error')
```

```r
effective_sensitivities(amounts, times, curve_times, zero_rates, bump = 1e-04, spread = 0, extrapolation = "error")
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `amounts` | Explicit cashflow amounts in one currency, matching times. Signed cashflows are accepted by PV methods; bond yield analytics require nonnegative future payments. |
| `times` | Explicit year coordinates relative to the valuation date. Curve nodes must be strictly increasing; floating-coupon starts/ends/resets follow the documented in-advance convention. |
| `curve_times` | Explicit year coordinates relative to the valuation date. Curve nodes must be strictly increasing; floating-coupon starts/ends/resets follow the documented in-advance convention. |
| `zero_rates` | Continuously compounded decimal zero rates at the supplied curve nodes. Rates may be negative; no implicit zero floor is imposed. |
| `bump` | Positive decimal parallel zero-curve perturbation for analyst finite differences; the default 0.0001 is one basis point. |
| `spread` | Explicit decimal spread. spread shifts the continuous discount curve; margin is added to the floating index coupon. |
| `extrapolation` | error rejects cashflows outside the curve; flat_zero explicitly extends the endpoint zero rates. |

Method contract: `ANALYTIK_ERGAENZUNGEN.md`.

Limitations: Signed offsetting cashflows may make relative measures unstable; this is not a regulatory stress decision

## equivalent_cap_rate

Find an explicitly bounded result-equivalent capitalization rate, BelWertV §25(5).

```python
equivalent_cap_rate(net_income, target_value, land_value, years, lower, upper, *, short_life_method=None, tolerance=1e-10, max_iterations=256)
```

```r
equivalent_cap_rate(net_income, target_value, land_value, years, lower, upper, short_life_method = NULL, tolerance = 1e-10, 
    max_iterations = 256)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `net_income` | Sustainable annual income in currency units; net_income already reflects the deductions required by the chosen method, unless explicitly used to solve an equivalent rate. |
| `target_value` | Independently established target income value, including all required cost deductions, for capitalization-rate equivalence. |
| `land_value` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `years` | Explicit duration or age in years. This is not a date or a number of days; method-specific age/life limits are checked. |
| `lower` | Explicit numerical search bracket. The function rejects an unbracketed target and never silently expands the interval. |
| `upper` | Explicit numerical search bracket. The function rejects an unbracketed target and never silently expands the interval. |
| `short_life_method` | For remaining life below 30 years: capitalize_land or, where supported, deduct_demolition. Standard long-life valuation rejects this argument. |
| `tolerance` | Positive convergence tolerance under the function's documented price/value residual convention. |
| `max_iterations` | Positive whole-number iteration limit; failure to converge raises NO_CONVERGENCE. |

Method contract: `ANALYTIK_ERGAENZUNGEN.md`.

Limitations: Target value must independently include required costs; no method eligibility is inferred

## ship_construction_value_check

Compare a proposed value to the externally confirmed construction-state value.

```python
ship_construction_value_check(proposed_value, confirmed_state_value, market_value, *, confirmation_status)
```

```r
ship_construction_value_check(proposed_value, confirmed_state_value, market_value, confirmation_status)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `proposed_value` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `confirmed_state_value` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `market_value` | Explicit monetary value in the common calculation currency. Valuation bases, scope and expert evidence must be consistent with the selected method. |
| `confirmation_status` | Explicit external assessment: MET, NOT_MET or MISSING. The function preserves missing/negative evidence rather than inventing approval. |

Method contract: `ANALYTIK_ERGAENZUNGEN.md`.

Limitations: State value and construction progress must be confirmed by the yard or technical expert; no statutory linear-progress formula is assumed

## transport_valuation_review

Annual ship/aircraft monitoring and deterioration/90-day arrears review triggers.

```python
transport_valuation_review(kind, as_of, last_monitoring, material_deterioration, material_arrears_days)
```

```r
transport_valuation_review(kind, as_of, last_monitoring, material_deterioration, material_arrears_days)
```

Input definitions below are part of the method contract. Consult the returned intermediate values and limitations; external legal qualifications and valuations are explicit prerequisites.

| Parameter | Meaning |
|---|---|
| `kind` | Pfandbrief kind: HYP (mortgage), OEF (public sector), SCH (ship), or FLG (aircraft); transport-only methods accept SCH/FLG. |
| `as_of` | Calculation/validity date, canonical YYYY-MM-DD; R also accepts a Date scalar. Not a timestamp. |
| `last_monitoring` | Date of the last completed value monitoring; the annual deadline is obtained by adding 12 calendar months. |
| `material_deterioration` | Explicit Boolean appraisal of material deterioration in valuation fundamentals; true triggers a review. |
| `material_arrears_days` | Whole number of days of material payment arrears. The review trigger is at least 90 days, subject to the stated property exception. |

Method contract: `ANALYTIK_ERGAENZUNGEN.md`.
