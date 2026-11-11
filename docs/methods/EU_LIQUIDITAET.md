# Pfandbriefbezogene EU-Einordnung und Liquiditätspuffer

Arbeitsgrundlage: lokale CRR-Fassung vom 26.06.2026, Artikel 129;
LCR-Fassung vom 08.07.2022, Artikel 9–12; PfandBG §§ 4 Absatz 1a und 41a.
Der Umfang ist auf Pfandbriefrechnungen begrenzt.

`covered_bond_risk_weight` bildet Artikel 129 Absätze 4 und 5 ab.
Voraussetzung ist die separat festgestellte Eignung. Die Ratingstufen
1/2/3/4/5/6 ergeben 10/20/20/50/50/100 Prozent. Ohne Rating werden die
Emittentenrisikogewichte 20/30/40/50/75/100/150 Prozent auf
10/15/20/25/35/50/100 Prozent abgebildet. Andere Werte werden nicht interpoliert.
Bei fehlender oder negativer Eignung wird kein privilegiertes Gewicht zugewiesen.

`crr_pool_check` prüft Nominaldeckung, Überdeckung und Bankpositionsgrenzen.
Die Standardüberdeckung beträgt 5 Prozent; eine belegte nationale Absenkung
kann bis mindestens 2 Prozent berücksichtigt werden. Bankpositionen mit CQS 1
sind bis 15 Prozent, CQS 2 bis 10 Prozent und CQS 3 bis 8 Prozent zulässig.
Zusammen gelten 15 Prozent, für CQS 2 und 3 zusammen 10 Prozent. Zugeordnete
Mindestüberdeckungsanteile und geeignete Abwicklungsforderungen sind ausdrücklich
ausgenommen; Freistellungen dürfen denselben Betrag nicht mehrfach verbrauchen.
CQS 3 verlangt zugelassene Derivate oder qualifizierte Liquiditätseinlagen mit
ursprünglicher Laufzeit von höchstens 100 Tagen.

Weitere Voraussetzungen aus Artikel 129, darunter Sicherheitenarten,
Einzeldarlehensgrenzen sowie Bewertung und Überwachung nach Artikeln 208 und
229, sind Teil des vollständigen externen Eignungsnachweises. Ein bestandener
Limitvergleich allein begründet diese Eignung nicht. Pro Aufruf wird eine
homogene Emissionskohorte geprüft. Emissionen vor 31.12.2007 bzw. vor 08.07.2022
haben unterschiedliche Ausnahmen und benötigen ausdrücklich belegten Altbestand.
Sollfall: Bondnominal 100, Assets 105; CQS-1/2/3-Beträge 5/2/8 bestehen;
CQS-2-Betrag 2.01 verletzt die gemeinsame Grenze von CQS 2 und 3.

`european_label` ordnet qualifizierten deutschen Pfandbriefen nach dem
07.07.2022 die europäische Bezeichnung zu; Premium ist HYP, OEF und SCH
vorbehalten. Das Label allein ist keine vollständige CRR-Eignungsprüfung.

`covered_bond_lcr` prüft jede Kandidatenklasse anhand ausdrücklicher
True/False/None- bzw. TRUE/FALSE/NULL-Bedingungen und weist MET, NOT_MET oder
MISSING aus. Die beste vollständig erfüllte Klasse wird ausgewählt;
ungeklärte bessere Klassen bleiben sichtbar.

| EU-Klasse | Mindestgröße | Bonität | Mindestüberdeckung | Haircut |
|---|---:|---|---:|---:|
| Level 1 | 500 Mio. EUR | CQS 1 oder zulässiger unrated-RW 10% | 2% | 7% |
| Level 2A | 250 Mio. EUR | CQS höchstens 2 oder zulässiger unrated-RW 20% | 7%, bei CQS 1 und Größe unter 500 Mio. EUR: 2% | 15% |
| Level 2B | 250 Mio. EUR | separate Anforderungen an Sicherheiten und zugrunde liegende Risikogewichte | 10% | 30% |

Level 2B setzt außerdem die vorgeschriebene monatliche Offenlegung voraus;
ein zusätzliches Ratingminimum wird Artikel 12 Absatz 1 Buchstabe e nicht
unterstellt. Für Drittstaaten gilt der eigene Level-2A-Zweig nach Artikel 11
Absatz 1 Buchstabe d mit Rechts-, Aufsichts-, Sicherheiten- und Transparenznachweis,
CQS 1 bzw. zulässigem unrated-RW 10 Prozent, Überdeckung 7 Prozent oder bei
mindestens 500 Mio. EUR Emissionsvolumen 2 Prozent.

`liquid_buffer_value` wendet auf den belegten Marktwert die Mindesthaircuts
0/7/15/30/50 Prozent für Level 1 sonstige/Level 1 Pfandbriefe/Level 2A/
Level 2B Pfandbriefe/Level 2B sonstige an. Besondere Verbriefungs- und
Fazilitätskategorien brauchen einen explizit belegten Haircut. Ein zusätzlicher
FX-Haircut wirkt multiplikativ auf den Restwert. Zusammensetzungsgrenzen einer
Gesamtbank-LCR werden nicht automatisch auf den Pfandbriefpuffer übertragen.
Geeignete Bankguthaben dürfen eine Restlaufzeit von drei Kalendermonaten haben.
Sollfälle: 100 Level-1-Pfandbrief → 93; mit weiterem FX-Abschlag 10 Prozent →
83.7. Drei Monate ab 31.01.2026 enden am 30.04.2026; der 01.05. liegt außerhalb.
