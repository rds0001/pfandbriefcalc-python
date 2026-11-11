# Datenvertrag der integrierten Poolrechnung

`analyze_pool(kind,positions,oc_allocations,cashflows,buffers,fx_rates,evidence,
as_of,known_at,additional_nominal=0,additional_pv=0)`.

Jede Position: position_id,kind,category,currency,amounts,pv_base,pv_up,pv_down,
features,limits. Kategorien MORTGAGE/PUBLIC/SHIP/AIRCRAFT/SUBSTITUTE/DERIVATIVE/BOND.
Barwerte in der Positionswährung; positive Beträge bei Assets und Bonds,
Bankperspektive (vorzeichenbehaftet) bei Derivaten. Sie beziehen sich ausdrücklich
auf die jeweils zur Deckung bestimmte Tranche, nicht die gesamte Forderung.
Ein Derivate-Datensatz steht für genau einen rechtlich nettingfähigen Rahmenvertrag.

`amounts`: für Assets die benannten Parameter von cover_amount außercategory.
FürBonds nominal,max_redemption,own_held_excluded (bool). FürDerivate leer:
der aktuelle unabhängige Marktwert ist der Beendigungsanspruch/-verbindlichkeit.
`features`: explizite Liste der Auslands-/Treuhand-/Altbestandsmerkmale aus
required_evidence. guaranteed/partial/exception für abweichenden Beleihungssatz
werden zusätzlich aus Betragseingaben abgeleitet. PV-OC und Liquiditätsnutzung
werden aus der tatsächlichen Allokation abgeleitet. Ein Altbestand ersetzt nicht
den konkret belegten Übergangsvertrag und Regelprofil.

`limits`: für Assets/Derivate tier,bank_group,construction,land,foreign_bucket,
downgraded,liquidity_only,pv_oc_exempt (bool),pure_fx_hedge(bool, nurDerivate).
Primary folgt aus der Positionskategorie, Betrag aus cover_amount bzw.
positivemDerivatemarktwert. Freistellungsbetrag wird aus zugewiesenemPV-OC-Anteil
und bool abgeleitet. Die Einstufung ist obligatorisch nachzuweisen; bei fehlendem
Beleg ist der rechnerische Output hypothetisch/INCOMPLETE. Bond-limits leer.

`cashflows`: flow_id,position_id,date,inflow,outflow; Währung folgtPosition.
`buffers`: asset_id,qualified_value,monetized,qualification_ref inPositionswährung.
Die Qualifikation/Art9-Bewertung ist separat belegter Input. Die Position muss
ein anrechenbarer positiver Deckungswert sein; ausgeschlossene oder ungeeignete
Werte liefern keinePufferanrechnung. Pufferwerte dürfen denBasisbarwert
überschreiten(z.B.abweichenderMarktwert); es erfolgt kein ungesetzlicherBarwertcap.
`fx_rates`: currency,eur_per_unit,shock; fürEUR1/0. Vollständige Währungsabdeckung.
`oc_allocations`: asset_id,role,fraction gemäßpool_coverage.

Erforderliche Evidenz enthält zusätzlich denScopePOOL:<Gattung> mit
profile_applicability,complete_position_universe,valuation_method,
operational_governance und additional_requirements. Für diese Prüfpunkte sind
Geltung/Wissensstand, vollständiger Bestand, tägliche/wöchentliche Bewertung,
Kurven-/Optionenmodell/Methodenkontinuität, Erlaubnis/Treuhänder/Risikomanagement
und zutreffende erhöhte Anforderungen zu belegen. Dies sind externe
Nachweisverträge, keine erfundene automatische Institutsgenehmigung.

AlleEvidenzpflichten sind vor derBeurteilung ableitbar: `pool_requirements`.
BeiNOT_MET wird der positive Anspruch ausgeschlossen; negativeDerivatebeiträge
bleibenbestehen. BeiMISSING bleibt die Rechnung hypothetisch. EinEigenbestand
scheidet erst nachMETfürfeature_own_held aus; sonst bleibtVerbindlichkeit bestehen.
Durchberechnung bleibt verfügbar, auchwenn fachlichePrüfungen scheitern.

Unabhängiger Integrationssollfall: EUR-Pool mitPrimärdeckung100,NOM-OC2(HYP/OEF)
oder5(SCH/FLG),PV-OC2(zulässigesStaatspapier),Bond100,alleBarwertegleichNennwert,
keine180TageFälligkeiten, vollständige synthetischeBelege=>CHECKS_PASSED;
ohneBelege=>INCOMPLETE bei identischenhypothetischenRechenwerten.
AusgeschlossenerunbesicherterAusfall oderNOT_METfürPrimärwert=>FAILED.
Negativderivat mit fehlendemNachweis bleibt inBasis/Stress/Liquidität enthalten.
