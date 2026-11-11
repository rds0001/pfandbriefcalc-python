# pfandbriefcalc – Anwenderhandbuch

pfandbriefcalc stellt native Python- und R-Funktionen für Hypothekenpfandbriefe
(HYP), Öffentliche Pfandbriefe (OEF), Schiffspfandbriefe (SCH) und
Flugzeugpfandbriefe (FLG) bereit. Beide Pakete rechnen offline. R ruft kein Python
auf; Python ruft kein R auf. Es gibt keine App und keine amtliche Meldeeinreichung.

Herausgeber: RiskDataScience GmbH. Maintainer: Dr. Dimitrios Geromichalos,
riskdatascience@web.de. Lizenz: AGPL-3.0-only. Paketname in beiden Sprachen:
`pfandbriefcalc`; vorgesehene Repositorynamen: `pfandbriefcalc-python` und
`pfandbriefcalc-r`. Eine lokale Installation ist keine Veröffentlichung.

## Installation und erster Durchlauf

Python benötigt mindestens Python 3.10 und keine zusätzlichen Laufzeitpakete.
Aus einem lokal bereitgestellten Wheel:

```sh
python -m pip install --no-index /pfad/pfandbriefcalc-0.1.0-py3-none-any.whl
```

```python
from pfandbriefcalc import cashflow_example_pool, analyze_pool, pool_metrics

example = cashflow_example_pool("HYP")
result = analyze_pool(**example.value)
print(result.value)
print(result.details["liquidity"]["value"])
metrics = pool_metrics(result)
```

R benötigt mindestens R 4.1. Aus dem lokalen Quellpaket:

```r
install.packages("/pfad/pfandbriefcalc_0.1.0.tar.gz", repos = NULL, type = "source")
library(pfandbriefcalc)
example <- cashflow_example_pool("HYP")
result <- do.call(analyze_pool, example$value)
result$value
result$details$liquidity$value
metrics <- pool_metrics(result)
```

Die vier Gattungen sind durch Ersetzen von `HYP` durch `OEF`, `SCH` oder `FLG`
zugänglich. Die Beispiele enthalten ausdrücklich **fiktive** Gutachten- und
Rechtsnachweise. Sie dürfen nicht als echte Nachweise übernommen werden.
Die vereinfachte Variante `example_pool(kind, scale=1)` hat bei einem Bond von 100
Deckungswerte von 104 für HYP/OEF beziehungsweise107 für SCH/FLG. Die
Cashflowvariante verwendet unter anderem jährliche Aktivcoupons, vierteljährliche
Bondcoupons, eine explizite 3%-Zerokurve und gesetzliche statische Zinsschocks.
Ihr erster Coupon verursacht einen 180-Tage-Bedarf von einer Skaleneinheit.

## Ergebnisse und Fehler lesen

Alle Fachfunktionen liefern ein `CalcResult` in Python beziehungsweise einen
`pfandbrief_result` in R. Die Felder sind sprachübergreifend gleichwertig:

| Feld | Bedeutung |
|---|---|
| value | Zahl, Recordtabelle, Klassifikation oder fachlicher Prüfstatus |
| method | Stabile Bezeichnung der angewendeten Funktion |
| sources | Zugeordnete Normfundstellen oder ausdrücklich benannte Rechenkonvention |
| unit | Währung, Quote, Zins, boolescher Wert oder Records |
| status | `CALCULATED`: Die Funktion wurde technisch ausgeführt |
| details | Zwischenwerte, Auswahlentscheidungen, Prüfungen und atomare Beiträge |
| limitations | Konkrete Grenzen der Methode und der zu erbringenden Nachweise |

`CALCULATED` bedeutet **nicht**, dass eine Deckungs- oder Eignungsprüfung
bestanden wurde. Der integrierte Prüfstatus steht in `result.value`:

- `CHECKS_PASSED`: Die implementierten Prüfungen und übergebenen Nachweisurteile
  sind erfüllt. Dies authentifiziert keine Belege und ist keine Aufsichtsfreigabe.
- `INCOMPLETE`: Ein notwendiger Nachweis fehlt, ist noch nicht bekannt oder gilt
  am Stichtag nicht. Die ausgewiesenen Rechenwerte bleiben hypothetisch.
- `FAILED`: Mindestens eine numerische oder belegte Eignungsprüfung scheitert.

Einige Einzelmethoden verwenden zusätzlich `REVIEW_REQUIRED` oder `INELIGIBLE`.
Details benennen den konkreten Anlass. Fehlende Beträge sind `None`/`NULL`, nicht
null Euro. `NaN`, Unendlich, R-`NA` und stilles Vektorrecycling werden nicht als
zulässige Recheneingaben behandelt.

Python wirft `PfandbriefError` mit `.code`; R verwendet die Fehlerklasse
`pfandbrief_error` mit `$code`. Beispiele sind `MISSING_FIELD`, `KIND_MISMATCH`,
`OVERALLOCATION`, `NO_BRACKET` und `MISSING_FIXING`. Eine ungültige Datentabelle
ist ein Eingabefehler; ein korrekt berechneter Deckungsverstoß ist ein Ergebnis.

## Eigene Daten und Nachweise

Beginnen Sie mit dem [Datenvertrag](DATA_CONTRACTS.md), nicht mit einer Änderung
der fiktiven Nachweisurteile. `pool_requirements` erzeugt die aus Ihren tatsächlichen
Positionen, Überdeckungszuordnungen und Puffern abgeleiteten Pflichtnachweise.
Erfassen Sie anschließend reale datierte Beurteilungen. Ohne diese liefert die
Berechnung nachvollziehbare Zahlen und gegebenenfalls `INCOMPLETE`.

```python
from pfandbriefcalc import pool_requirements, analyze_pool

# inputs: eigener, nach DATA_CONTRACTS.md aufgebauter Eingabebestand
# required = pool_requirements(inputs["kind"], inputs["positions"],
#                              inputs["oc_allocations"], inputs["buffers"])
# inputs["evidence"] = eigene_datierte_nachweise
# result = analyze_pool(**inputs)
```

`as_of` ist das Geltungs-/Berechnungsdatum; `known_at` ist der Wissensstichtag.
Korrigierte Regeln und Nachweise werden zuerst nach dem neuesten bekannten Stand
ausgewählt und erst dann auf Geltung geprüft. Eine korrigierte Geltungsdauer
reaktiviert keine überholte alte Fassung. `select_rule_profile` verwaltet explizit
übergebene Profile; die Library beschafft und authentifiziert keine Rechtsprofile.

Die integrierte Rechnung verwendet die in den Methoden beschriebenen Parameter
des lokal dokumentierten Rechtsstands. Ein historisches Datum schaltet diese
Parameter **nicht automatisch** um. Historische Sonderfälle benötigen ein
passendes explizites Profil und gegebenenfalls die konfigurierbaren Einzelmethoden.
Die konkret implementierten CRR-Altbestandszweige und Registerfeldverträge sind
in ihren APIs ausgewiesen. Es gibt keinen behaupteten vollständigen historischen
Rechtsdatenbankdienst.

## Beleihungswerte und Anrechnung

Die Wertmethoden trennen nachhaltige Erträge, Bewirtschaftungskosten,
Kapitalisierung, Bodenwert, Restnutzungsdauer und Wertabschläge. Ein aktueller
BaFin-Kapitalisierungszinssatz muss als belegter Parameter übergeben werden.
Die archivierte Mitteilung ersetzt keine automatische Stichtagsprüfung.

```python
from pfandbriefcalc import income_value, cover_amount

value = income_value(10000, 50000, 0.05, 40)
used = cover_amount("MORTGAGE", claim=80000, registered=75000,
                    redemption=80000, defaulted=False, guaranteed=False,
                    guarantor_defaulted=False, lien=80000,
                    lending_value=100000, prior_claims=10000)
assert used.value == 50000
```

`income_value` benötigt bereits sachgerecht bereinigten Jahresreinertrag.
Bei Restnutzungsdauer unter 30 Jahren sind die zulässigen Alternativen ausdrücklich
auszuwählen. Nichtpositiver Gebäudereinertrag hat einen eigenen Bodenwertzweig.
`operating_costs` rechnet Komponentenminima, die relevante 15%-Untergrenze und
tatsächlich höhere Gesamtkosten auseinander. Akute Mietausfälle sind zusätzliche
Wertkorrekturen; Kosten dürfen nicht zweimal abgezogen werden.

Die Verwaltungskostenindexierung verwendet kompatible Oktoberindizes und rundet
den Jahresbetrag mit exakter Dezimalrechnung auf volle Euro. CPI-Werte dürfen
höchstens 15 signifikante Dezimalstellen haben; zusätzliche Genauigkeit wird
als Eingabefehler zurückgewiesen. `dwelling` steht für die einschlägige
Wohnungs-/Ein- oder Zweifamilienhausbasis, `condominium` für Eigentumswohnungen,
`garage` für Garagen/Stellplätze gemäß der zugrunde gelegten Regel.

Schiffs- und Flugzeugfunktionen berechnen Obergrenzen aus den ausdrücklich
vorliegenden Markt-, Historien- und Preisangaben. Bei fehlenden Marktangaben ist
ein belegtes alternatives Bewertungsverfahren erforderlich. Der Zustandswert
eines Schiffsbauwerks stammt aus dem bestätigten Bautenstand; die Library erfindet
keine gesetzliche Formel „Baufortschritt mal Fertigwert“. Die förmliche Bewertung
und Wertfestsetzung bleibt Aufgabe der zuständigen qualifizierten Personen.

## Cashflows, Zinskurven und Stress

Zinsen sind Dezimalzahlen: 0.025 entspricht 250 Basispunkten. Die Kurvenfunktionen
verwenden kontinuierlich verzinste Zeroraten und lineare Interpolation der
Zeroraten. Eine Extrapolation muss ausdrücklich als `flat_zero` gewählt werden;
standardmäßig führen Cashflows außerhalb der Kurve zu einem Fehler.

```r
schedule <- coupon_schedule("2026-11-11", "2028-11-11", 4,
                            "30E/360", "modified_following", character())$value
cash <- contract_cashflows(schedule, 1000000,
                           rep(.04, length(schedule)), rep(0, length(schedule)))
```

`contract_cashflows` verarbeitet periodenspezifische Coupons und Tilgungen;
die Restschuld wird am Ende zurückgezahlt. `project_floating_coupons` trennt
tatsächliche Fixings von zukünftigen Forwardprojektionen. Forecast- und
Diskontkurve können getrennt übergeben werden. Für Floating-Rate-Stress sind die
Coupons je Szenario neu zu projizieren; die Funktion `cashflow_scenarios` hält
ihre ausdrücklich übergebenen Cashflowbeträge fest.

`rate_shocks` implementiert statische und dynamische Zinsverfahren; bei der
dynamischen Variante sind 250 historische Beobachtungen und die vorgeschriebenen
Stützstellen erforderlich. Standardabweichungskonvention und Historie sind
explizit. `pool_stress` verrechnet zunächst die Aktiv-/Passivbarwerte je Währung
und wendet dann den adversen Wechselkursschock auf den Nettobetrag an. Keine
Verrechnung zwischen unterschiedlichen Pfandbriefgattungen.

Optionswerte und Derivate werden nicht durch eine gewöhnliche Bond-Diskontierung
ersetzt. Die integrierte Rechnung benötigt für Derivaterahmenverträge unabhängig
ermittelte Marktwerte in allen Szenarien. Zukünftige Optionsausübungen und
abweichende Vertragsbedingungen sind ausdrückliche Szenarioeingaben.

## Deckung, Überdeckung und Liquidität

Die nominale und barwertige sichernde Überdeckung haben getrennte Zuordnungen.
Der gleiche Assetanteil kann nicht beiden Rollen zugeordnet werden. Zusätzlich
wird geprüft, ob nach den Reservierungen noch genügend nominale Grunddeckung
vorhanden ist. Ein ausreichender Gesamtdeckungsquotient allein genügt nicht.

Die Limite haben jeweils ihre eigene Bezugsgröße: Pfandbriefnennumlauf,
Gesamtdeckungswerte, primäre Sicherheiten oder geschützte Auslandsforderungen.
Die Software überträgt eine Freistellung nicht pauschal auf andere Limits.
Die OEF-Rechnung hat keine allgemeine 20%-Ersatzdeckungsgrenze.

`liquidity_180` enthält genau 180 folgende Kalendertage einschließlich Nulltagen.
Der schlechteste kumulierte Saldo bestimmt den Bedarf; der Saldo am Horizontende
allein reicht nicht aus. `liquid_buffer_value` unterstützt die ausgewiesenen
LCR-Haircuts beziehungsweise geeignete Bankguthaben innerhalb von drei
Kalendermonaten. Ein für den Puffer monetisierter Wert kann nicht zugleich mit
unveränderten Vertragszuflüssen als zusätzliche Liquiditätsquelle eingehen.

`extension_plan` verändert den Basisplan nicht. Es prüft ein ausdrücklich
vorgegebenes Sachwalterszenario einschließlich maximaler Verschiebungsdauer und
Tilgungsreihenfolge. `interest_extension` behandelt die besondere Zinsverschiebung
im ersten Monat. Rechtsvoraussetzungen, vollständiger Emissionsumfang und
abweichende Verträge bleiben datierte Nachweise.

## Kennzahlen und Exporte

`pool_metrics` verwendet die Ergebnisse derselben Poolrechnung. Ergänzend stehen
Aggregation, Kalenderlaufzeitbänder, gewichteter Beleihungsauslauf und explizite
numerische Abstimmung zur Verfügung. Bei mehreren verwendeten Hypotheken auf
demselben Grundstück wird für den Beleihungsauslauf die vorgeschriebene Auswahl
des höchsten Auslaufs berücksichtigt. Der volle Darlehensauslauf ist kein Ersatz
für den gesetzlich definierten Deckungsauslauf.

```python
from pfandbriefcalc import export_table
# Nur ein ausdrücklich gewähltes eigenes Ziel verwenden:
# export_table(metrics.value, "/eigener/pfad/kennzahlen.csv")
```

```r
# export_table(metrics$value, "/eigener/pfad/kennzahlen.csv")
# saveRDS(result, "/eigener/pfad/vollstaendiges_ergebnis.rds")
```

CSV ist eine flache Austauschdarstellung; leere Felder repräsentieren fehlende
Werte. Python kann das vollständige Ergebnis mittels `result.as_dict()` und
Standard-JSON serialisieren, R mittels `saveRDS`. Die Methoden erzeugen keine
XBRL-, MVP- oder sonstigen amtlichen Einreichungsdateien.

## Quellenstand, Reproduzierbarkeit und Grenzen

Die Umsetzung basiert auf dem akzeptierten lokalen Dokumentationsbestand.
`SOURCES.json` beschreibt Fassungen und Prüfsummen, ohne fremde Gesetzes-PDFs
oder das Entwicklungsscaffold in die Distributionen aufzunehmen. Die Library
lädt keine Gesetze, Marktdaten, CPI-Zeitreihen oder Kalender nach.

Für eine reproduzierbare Anwendung sind Paketversion, Eingaben, Kurven,
Szenarien, Profile, Geltungs-/Wissensdaten und echte Belege gemeinsam aufzubewahren.
Python und R verwenden IEEE-754-Gleitkommazahlen; fachliche Grenzentscheidungen
werden nicht durch ein allgemeines Epsilon gelockert. Numerische Abstimmung und
Solver haben separat ausgewiesene Toleranzen.

Die Berechnungen ersetzen keine Gutachten, Rechtsfeststellungen, Genehmigungen
oder Institutsprüfung. Ein externer Nachweis ist ein prüfbarer Eingabevertrag,
keine von der Software selbst erteilte Bescheinigung. Unterstützte Rechenmodelle
und ihre Grenzen sind in der [API-Referenz](API_REFERENCE.md) dokumentiert.
