# pfandbriefcalc

[![CI](https://github.com/rds0001/pfandbriefcalc-python/actions/workflows/ci.yml/badge.svg)](https://github.com/rds0001/pfandbriefcalc-python/actions/workflows/ci.yml)

Native offline calculations for Hypothekenpfandbriefe (HYP), Öffentliche
Pfandbriefe (OEF), Schiffspfandbriefe (SCH) and Flugzeugpfandbriefe (FLG).
Publisher: RiskDataScience GmbH. Maintainer: Dr. Dimitrios Geromichalos
<riskdatascience@web.de>. License: AGPL-3.0-only. Version 0.1.0.

The library covers lending-value calculations, contractual cashflows, curve/FX
stress, coverage and limits, 180-day liquidity, evidence controls, selected
EU classifications, deferral scenarios and local analytical exports.
Calculation success is separate from eligibility and legal approval. External
valuations, classifications and approvals are explicit evidence inputs.
Historic dates do not automatically select historical legislation.

Python >= 3.10; no third-party runtime dependencies. Install the local wheel
with `python -m pip install --no-index /path/pfandbriefcalc-0.1.0-py3-none-any.whl`.

```python
from pfandbriefcalc import cashflow_example_pool, analyze_pool, pool_metrics
inputs = cashflow_example_pool("HYP").value  # explicitly fictional evidence
result = analyze_pool(**inputs)
print(result.value)
metrics = pool_metrics(result)
```

All 68 functions return `CalcResult`; input errors raise `PfandbriefError` with
an explicit code. Decimal rates, unrounded currency amounts, explicit calendars.
[Handbook](docs/HANDBOOK.md), [API reference](docs/API_REFERENCE.md),
[data contracts](docs/DATA_CONTRACTS.md), [source metadata](docs/SOURCES.json).
The same documents are installed in `pfandbriefcalc/resources`.
