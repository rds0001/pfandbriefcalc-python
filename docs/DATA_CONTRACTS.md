# pfandbriefcalc record contracts

Python tables are lists of dictionaries. R tables are lists of named lists;
most simple tables also accept data frames. Nested columns should remain list
columns. Use `None` in Python and `NULL` in R for explicitly absent fields;
do not use R `NA` as a substitute. An R `NULL` element must be retained with
`list(key=NULL)` or `x["key"] <- list(NULL)` rather than deleted with `$key <- NULL`.

All IDs are nonempty text and unique under the method's declared key. Booleans
are real `True`/`False` or `TRUE`/`FALSE`, not 0/1. Rates and fractions are decimal.
Dates are canonical YYYY-MM-DD. Cashflow year coordinates are numbers in years.
Tables contain no implicit exchange-rate conversion, except `analyze_pool`, which
explicitly converts through its supplied `fx_rates` table.

## Integrated positions: analyze_pool

Every record has these fields:

| Field | Contract |
|---|---|
| position_id | Unique ID across assets, bonds and derivative frameworks |
| kind | HYP, OEF, SCH or FLG; the entire call has exactly one kind |
| category | MORTGAGE, PUBLIC, SHIP, AIRCRAFT, SUBSTITUTE, DERIVATIVE or BOND |
| currency | Currency ID matching exactly one FX row |
| amounts | Category-specific mapping described below |
| pv_base, pv_up, pv_down | Qualified-tranche PV in position currency; positive for assets/bonds, bank-signed for derivatives |
| features | Explicit feature list, empty only when genuinely inapplicable |
| limits | Asset/derivative classification mapping; empty for bonds |

MORTGAGE/PUBLIC/SHIP/AIRCRAFT are the primary categories for HYP/OEF/SCH/FLG
respectively. A public-sector security used as additional HYP cover is SUBSTITUTE,
not an OEF primary asset accidentally inserted into a HYP pool.

For assets, `amounts` contains `claim,registered,redemption,defaulted,guaranteed,
guarantor_defaulted`. Secured primary assets additionally need `lien,lending_value,
prior_claims`; guaranteed claims need `guarantee_amount`. Optional `lending_limit`
is regular0.60; a different explicit limit creates an exception-evidence requirement.
The computed amount is capped by claim, registration, redemption and qualified
collateral/guarantee capacity. Default exclusions follow the documented secured/
guaranteed distinctions. Positive PVs must value this computed eligible tranche;
the library does not automatically scale the whole-loan PV by a nominal ratio.

For bonds, `amounts` has `nominal,max_redemption,own_held_excluded`. Maximum known
redemption replaces nominal when higher. Exclusion of an own-held bond requires
the corresponding positive evidence; without it the liability remains included.
For derivatives, `amounts` is empty. The independent signed base market value is
the framework closeout claim/liability. Each derivative row represents a separate
legally nettable framework, not arbitrary netting across counterparties.

Asset/derivative `limits` has:

| Field | Values / meaning |
|---|---|
| tier | PRIMARY, T1, T2, T3, T4 or UNLIMITED; no OEF T4 |
| bank_group | Relevant bank group ID or explicit None/NULL when not applicable |
| construction, land | Explicit Booleans; land only for HYP |
| foreign_bucket | NONE, PRIMARY_PROTECTED, PRIMARY_UNPROTECTED, OTHER_PROTECTED, OTHER_UNPROTECTED |
| downgraded | Whether the special public-claim downgrade/grandfathering limit applies |
| liquidity_only | Exclusively registered for liquidity purposes, with distinct statutory exemptions |
| pv_oc_exempt | Whether the category permits the explicit PV-OC share to be exempted from the corresponding cumulative tier limits |
| pure_fx_hedge | Mandatory Boolean for derivatives; excluded from the12% liability limit only |

Tier assignments and foreign protection are evidenced classifications. They are
not inferred solely from a CQS, country string or issuer name. Protected and
unprotected buckets must describe the complete relevant denominator population;
`NONE` does not create a denominator. OEF combines its protected primary and
other public claims for its applicable foreign-priority test.

`features` accepts `foreign,partial,refinancing,guaranteed,pv_oc,liquidity,legacy,
exception,own_held,payment_settlement`. The integrated driver additionally derives
guaranteed/partial/exception from amount inputs and OC/liquidity/own-held features
from their actual use. It cannot discover undisclosed foreign or fiduciary facts.

## OC, FX, flows and buffers

`oc_allocations`: `asset_id,role,fraction`, where role is NOMINAL_OC or PV_OC.
Fractions of the same physical value sum to at most one. This is a checked explicit
allocation, not an optimizer. Qualifying PV-OC instrument types are evidenced
separately; derivatives cannot serve that role.

`fx_rates`: `currency,eur_per_unit,shock`. Every currency needs one explicit row,
including EUR with rate1 and shock0. Static/dynamic shocks can be calculated
separately with `fx_shock`. Positive and negative currency nets receive adverse
conversion in opposite directions.

`cashflows`: `flow_id,position_id,date,inflow,outflow`. The driver derives currency
from the position and converts to EUR. IDs must reference the same complete
position universe. Outflows from negative or unproven derivative positions remain.
The elementary `liquidity_180` instead expects already homogeneous amounts.

`buffers`: `asset_id,qualified_value,monetized,qualification_ref`. The qualified
value is in position currency. Use the separately qualified result of
`liquid_buffer_value`; an incomplete qualification returns a missing amount and
must not be passed as zero. Monetary buffer amounts need not equal discount-curve
PVs. Positive contractual inflows of monetized assets are excluded to avoid an
inconsistent double use. Neither derivative positions nor bond liabilities are
eligible buffer records.

## Evidence and rule profiles

`required_evidence` derives the position requirements. `pool_requirements` adds
pool-wide scope `POOL:<kind>` requirements for profile applicability, completeness
of the position universe, valuation methodology, governance and additional cover
requirements. It returns the exact list accepted by `assess_evidence`.

Requirement rows: `requirement_id,scope,allow_not_applicable,source_ref`.
Evidence rows: `evidence_id,requirement_id,scope,valid_from,valid_to,known_from,
conclusion,reviewer,source_ref,reason`. Conclusion is MET, NOT_MET or
NOT_APPLICABLE. Each evidence identity may have successive knowledge-date revisions;
its requirement and scope cannot change. Conflicting active conclusions are errors.
Missing, future and expired evidence remain separate atomic outcomes. A false
NOT_APPLICABLE assertion cannot waive a mandatory requirement.

Profile rows: `profile_id,revision,valid_from,valid_to,known_from,status,source_ref,
parameters`; status is VERIFIED or EXPERIMENTAL. Parameters are an explicit mapping.
Latest-known revision is selected before validity is tested. Profile source and
review status are supplied provenance; arbitrary user data does not become
authenticated legal authority by being marked VERIFIED.

## Elementary pool tables

- `pool_coverage` assets: `asset_id,kind,nominal,present_value,pv_oc_eligible`.
  Liabilities: `liability_id,kind,type,nominal,max_redemption,present_value`, with
  type BOND or DERIVATIVE. All amounts are nonnegative and already qualified.
- `pool_limits` assets: `asset_id,kind,amount,tier,pv_oc_exempt_amount,
  liquidity_only,bank_group,primary,construction,land,foreign_bucket,downgraded`.
  Derivative liabilities: `liability_id,kind,present_value,pure_fx_hedge`.
- `pool_stress` valuations: `position_id,kind,currency,scenario,signed_present_value`.
  Every position appears exactly once in BASE, UP and DOWN, in the same currency.

Elementary arithmetic does not automatically perform the integrated evidence
assessment. The result explicitly states that qualified amounts are prerequisites.

## Allocation and analytical register history

`validate_allocations` claims: `claim_id,capacity,currency,kind`; collateral:
`collateral_id,capacity,currency,kind`; edges:
`allocation_id,claim_id,collateral_id,kind,currency,amount`. Amounts cannot exceed
either node's independently established qualified capacity. The function does not
resolve legal priority or optimize allocations.

`register_snapshot` events: `event_id,asset_id,kind,effective_date,recorded_at,
sequence,action,payload,reason,evidence_ref`. Actions are ADD, UPDATE, REMOVE;
UPDATE replaces the full payload, REMOVE requires an empty payload. The knowledge
date `recorded_at` is an analytical audit field, not permission to backdate a
legal entry. Sequence numbers disambiguate events on the same effective date.

## Proposed legal-register admissions

`validate_register_entries` records: `entry_id,kind,register_id,number,entry_date,
recorded_date,category,fields,features`. `used_numbers` has `kind,register_id,number`
for all previously used numbers, including deleted entries. `recorded_date` here
means the actual admission date and must equal `entry_date`; it is distinct from
the analytical history's knowledge cutoff.

All current entries require `file_ref`. Secured primary `fields` additionally
require `object_ref,lending_value,lien_ref,lien_currency,lien_nominal`.
Public/substitute entries require `debtor,claim_ref,currency,nominal`. Derivatives
require `counterparty_name,counterparty_address,product_terms,counterparty_ref,
framework_date,trade_date,original_tenor,maturity,collateral_details,
trustee_consent_ref`. An explicitly documented absence of collateral can be
represented as text such as NONE, not a missing mandatory field.

Conditional register features add the following fields:

| Feature | Additional fields |
|---|---|
| non_accessory | claim_debtor,claim_currency,claim_nominal,loan_ref |
| guaranteed | guarantor |
| partial | assigned_part,relative_rank |
| refinancing | refinancing_institution,refinancing_timestamp,refinancing_legal_basis |
| fiduciary | transfer_creditor |
| insurance_assignment | insurance_security_ref |
| deposit | account_bank,iban |
| indemnity | indemnifier_name,indemnifier_address |
| sovereign_security | debt_form |

Historical entries before2023-07-01 require explicit `legacy_fields` and
`legacy_source_ref`. They do not silently inherit the current field contract.
These checks establish field presence, number conservation and date consistency;
legal meaning and completeness of all conditional features remain evidenced facts.

## EU and liquidity-specific tables

`crr_pool_check` bank rows: `exposure_id,amount,cqs,oc_amount,settlement_amount,
category,original_days,approved`. Category is NORMAL, LIQUIDITY_DEPOSIT or
DERIVATIVE. Exemptions are disjoint and bounded by the exposure; the total
minimum-OC exemption cannot exceed the applicable required OC amount. CQS3
liquidity deposits need original maturity at most100days; derivative use needs
the applicable approval. Other Art129 eligibility is independently evidenced.

`covered_bond_lcr` condition keys are `covered_bond_definition,bank_exposures,
level2b_collateral,level2b_underlying_rw,monthly_disclosure,third_country_law,
equivalent_supervision,third_country_collateral,transparency`. Only conditions
relevant to a candidate class are required, and missing ones remain visible.
Current issuer risk weights are supplied inputs, not calculated by a general
RWA engine. The locally documented LCR/CRR editions must be checked for applicability.

## Metrics and output tables

`maturity_buckets`: `position_id,kind,currency,amount,date`; one kind/currency per
call. For assets the date is the contractual repricing date, for bonds maturity.
`weighted_ltv`: `position_id,property_id,allocated_amount,
used_lien_with_prior_equal,lending_value`. The numerator is the cover-used lien
plus prior/equal burdens, not the full borrower claim. Only the highest used lien
per property contributes. Equal maxima require explicit prior consolidation.

`aggregate_positions` requires `position_id` plus the explicitly named grouping
and amount fields. Group by currency and kind whenever the values differ.
`reconcile_totals` accepts named numeric mappings. `export_table` accepts
homogeneous scalar records and an explicit filename, with overwrite disabled
by default. Nested results should use the language's native serialization.
