# Ergänzende Bewertungs- und Zinsanalytik

Quellen: PfandBarwertV §§ 3–5, BelWertV § 25 Absatz 5,
SchiffsBelWertV §§ 13–14 und FlugBelWertV § 12. Reine Finanzmathematik ist
von gesetzlichen Methoden und externen Bewertungen getrennt.

`cashflow_scenarios` diskontiert dieselben expliziten Zahlungsströme unter
BASE, UP und DOWN. Die Kurvenverschiebung stammt aus `rate_shocks`.
Derivate benötigen unabhängige Marktwerte; Optionen benötigen passende
Szenariowerte. Bei variablen Coupons muss der Aufrufer die Cashflows für jedes
Szenario neu projizieren. Sollfall: 100 in einem Jahr bei Nullzins ergibt
100, 100 × exp(−0.025) und 100 × exp(0.025).

`project_floating_coupons` verwendet für bereits erreichte Resets ausschließlich
übergebene Fixings. Für zukünftige In-advance-Resets gilt:
Forward = (DF(Start) / DF(Ende) − 1) / Couponjahrbruch.
Danach wird die Marge addiert; Floors und Caps wirken ausdrücklich entweder
auf den Index oder den gesamten Coupon. Projektions- und Diskontkurve können
verschieden sein. Sollfall: Periode von Jahr 1 bis Jahr 2 bei konstanter
Zerorate log(1.1) und Jahrbruch 1 ergibt Forward 0.1; mit Marge 0.02 und
All-in-Cap 0.11 ergibt sich Coupon 0.11. Resetzeitpunkt muss positiv sein.

`effective_sensitivities` bewertet unter paralleler kontinuierlicher
Zeroratenverschiebung ±bump neu. Duration = (PVdown − PVup)/(2 × PVbase × bump),
Konvexität = (PVdown + PVup − 2 × PVbase)/(PVbase × bump²),
DV01 = (PVdown − PVup)/(2 × bump) × 0.0001.
Ein Nullbarwert erlaubt keine relativen Kennzahlen. Dies ist Analystenrechnung.

`equivalent_cap_rate` löst `income_value(...) = target_value` innerhalb eines
expliziten Zinsintervalls. Der Zielwert ist unabhängig und nach korrektem
Kostenabzug bereitzustellen. Bei ewiger Rente gilt z = N / Zielwert.
Bei endlicher Laufzeit gilt der Standardzweig ab 30 Jahren oder ausdrücklich
`capitalize_land` unter 30 Jahren. Kein automatischer Abbruch-/Bodenwertzweig.
Sollfälle: N = 100, Ziel = 1000, ewige Rente → 0.1; N = 100, Boden = 0,
Restlaufzeit = 2, Ziel = 21000/121, `capitalize_land` → 0.1.

`ship_construction_value_check` begrenzt den vorgeschlagenen Wert durch den
bestätigten Zustandswert und Marktwert. Ein bestätigter Bautenstand ist externe
Eingabe; eine gesetzlich nicht vorgeschriebene lineare Baufortschrittsformel
wird nicht unterstellt. Fehlende Bestätigung ergibt INCOMPLETE.

`transport_valuation_review` prüft die jährliche Überwachung, wesentliche
Verschlechterung und wesentlichen Rückstand ab 90 Tagen. Die wohnwirtschaftliche
Eigennutzungsausnahme gilt hier nicht. Quellen: SchiffsBelWertV § 14 und
FlugBelWertV § 12.
