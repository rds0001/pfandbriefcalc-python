# Implementierter Kalkulationsumfang

Die beiden nativen Pakete enthalten 68 Fachfunktionen. Die folgenden Zuordnungen beschreiben Software und Eingabeverträge. Sie sind keine unabhängige Rechtsprüfung sämtlicher Normabsätze.

| Fähigkeit | Umsetzung / APIs |
|---|---|
| Regelprofile und zeitliche Auswahl | `select_rule_profile`, `assess_evidence` |
| Eingabevalidierung und Provenienz | `assess_evidence`, `validate_allocations` |
| Ertragswertbausteine | `annuity_factor`, `income_value`, `operating_costs`, `indexed_administration_cost`, `property_parameter_check` |
| Sachwertbausteine | `cost_value`, `linear_depreciation`, `construction_value_limit` |
| Vergleichswertbausteine | `comparison_value`, `property_value_check` |
| Verfahrenswahl und Wertableitung | `property_value_check` |
| Besondere Immobilienfälle | `small_loan_check`, `construction_value_limit`, `foreign_perpetuity_value`, `mortgage_terms_check` |
| Bewertungsnachweise und Überprüfung | `valuation_review`, `required_evidence`, `assess_evidence` |
| Schiffs- und Schiffsbauwerksbewertung | `ship_value_limit`, `ship_construction_value_check` |
| Schiffsbewertungskontrollen | `transport_valuation_review`, `required_evidence` |
| Flugzeugbewertung | `aircraft_value_limit` |
| Flugzeugbewertungskontrollen | `transport_valuation_review`, `required_evidence` |
| Hypothekarische Deckung | `cover_amount`, `secured_amount`, `mortgage_terms_check`, `insurance_check` |
| Öffentliche Deckung | `cover_amount`, `required_evidence`, `pool_limits` |
| Schiffsdeckung | `cover_amount`, `transport_loan_check`, `insurance_check` |
| Flugzeugdeckung | `cover_amount`, `transport_loan_check`, `insurance_check` |
| Weitere Deckungswerte | `pool_limits`, `liquid_buffer_value`, `required_evidence` |
| Deckungsderivate | `required_evidence`, `pool_limits`, `pool_stress` |
| Ausland und externe Rechtsnachweise | `required_evidence`, `assess_evidence`, `pool_limits` |
| Registerdaten und Ereignisse | `validate_register_entries`, `register_snapshot` |
| Sicherheitenallokation | `validate_allocations`, `secured_amount` |
| Treuhand und Refinanzierung | `validate_register_entries`, `required_evidence`, `assess_evidence` |
| Vertragscashflows | `year_fraction`, `adjust_date`, `coupon_schedule`, `contract_cashflows`, `project_floating_coupons` |
| Kurven und Währungen | `discount_factors`, `present_value`, `stressed_fx_net` |
| Pfandbriefpreis und Rendite | `bond_analytics`, `yield_to_maturity`, `accrued_interest` |
| Analystensensitivitäten | `effective_sensitivities`, `cashflow_scenarios` |
| Regulatorische Stressverfahren | `rate_shocks`, `fx_shock`, `pool_stress` |
| Modell- und Methodenprüfung | `pool_requirements`, `assess_evidence`, `select_rule_profile` |
| Managementszenarien | `cashflow_scenarios`, `equivalent_cap_rate`, `extension_plan` |
| Nennwertdeckung | `cover_amount`, `coverage_amounts`, `pool_coverage` |
| Barwertdeckung | `present_value`, `pool_coverage`, `pool_stress` |
| Limits und Überdeckung | `pool_limits`, `pool_coverage` |
| Liquiditätsdeckung | `liquidity_gap`, `liquidity_180`, `liquid_buffer_value` |
| Fälligkeit und Abwicklungsszenarien | `deferred_interest`, `interest_extension`, `extension_plan` |
| Poolintegration | `analyze_pool`, `pool_requirements` |
| Kennzahlendefinitionen und Aggregationen | `pool_metrics`, `aggregate_positions` |
| Numerische Transparenzkennzahlen | `maturity_buckets`, `weighted_ltv`, `pool_metrics` |
| Lokale Ergebnisexporte | `export_table` |
| Kennzahlenabstimmung | `reconcile_totals` |
| Erlaubnis, Aufsicht und Rollen | `pool_requirements`, `assess_evidence` |
| Risikomanagement und Treuhänder | `pool_requirements`, `required_evidence`, `assess_evidence` |
| Insolvenz, Schutz und Übertragung | `required_evidence`, `extension_plan`, `assess_evidence` |
| Bezeichnung und EU-Einordnung | `european_label`, `covered_bond_risk_weight`, `crr_pool_check`, `covered_bond_lcr` |
| Granulare APIs und Handbücher | API-Referenz, Handbuch und lokale Paketabnahme |
| Synthetische Profile und Referenzdaten | `example_pool`, `cashflow_example_pool` |
| Native Parität und Offlinepakete | API-Referenz, Handbuch und lokale Paketabnahme |

## Explizite Modellgrenzen

- Aktueller dokumentierter Methodenstand; keine automatisch gepflegte historische Rechtsdatenbank. Abweichende Rechtsprofile und Altbestandsausnahmen brauchen ausdrückliche Parameter und datierte Anwendbarkeitsnachweise.
- Statische und dynamische gesetzliche Zins-/FX-Verfahren sind implementiert. Individuelle Optionsmodelle, unabhängige Derivatmarktpreise und künftige Ausübungen werden als bewertete Szenarioeingaben angebunden.
- Immobilien-, Schiffs- und Flugzeugwerte verwenden explizite sachverständige Markt-, Zustands-, Einkommens- und Nutzungsdauerangaben. Die Library erzeugt keine Gutachten oder Marktpreiszeitreihen.
- CRR Art.129 unterstützt Tabellenzuordnung, Bankgrenzen, Überdeckung und die bezeichneten Altbestandszweige. Weitere Sicherheiten-, Bewertungs- und Rechtsvoraussetzungen bleiben explizite Eignungsnachweise. Kein allgemeines RWA-Modul.
- LCR unterstützt die beschriebenen Pfandbriefklassen und Einzelwert-Haircuts für den Pfandbriefpuffer. Keine Gesamtbank-LCR mit allen Zusammensetzungsgrenzen.
- Registerdatenkontrollen und analytische Ereignisrekonstruktion ersetzen kein rechtswirksames Deckungs- oder Refinanzierungsregister.
- Aufsichtliche Formulare, Fristen und elektronische Einreichungen sind gemäß Nutzerentscheidung ausgeschlossen. Kennzahlen, Abstimmungen und lokale Exporte sind enthalten.

Das lebende Norminventar ordnet 265 Abschnitte ein. Eine Zuordnung ist kein Nachweis vollständiger Satz-für-Satz-Abdeckung. Rechen-, Sprach- und Paketnachweise werden im lokalen Abnahmebericht getrennt ausgewiesen.
