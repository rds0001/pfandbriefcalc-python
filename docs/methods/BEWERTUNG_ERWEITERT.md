# Erweiterte Bewertungsbausteine

M020–M027. Quellen: BelWertV §§4,9–12,16–17,24–26 und Anlagen1–3 sowie
ImmoWertV Anlage3 in den lokalen Browsertexten. Keine ungeprüfte Übernahme
aktueller Index- oder BaFin-Bekanntgabewerte.

- Verwaltung Wohnnutzung: Basisbeträge230/275/30 für Wohnung/Eigentumswohnung/
  Garage multipliziert mit explizitem Oktober-VPI des Vorjahres geteilt durch
  Oktober2001-VPI, auf volle Euro kaufmännisch gerundet. Die Indizes müssen aus
  derselben Indexbasis stammen. Der Aufrufer liefert Indexquelle und Jahresbezug.
- Kosten: je Kostenart Maximum aus expliziter Schätzung und gesetzlicher
  Untergrenze. Verwaltung gewerblich>=1% Rohertrag; wohnwirtschaftlicher
  Mindestbetrag separat indexiert. Instandhaltung Herstellungskosten ohne
  Baunebenkosten/Außenanlagen *0.8/0.5/0.4% je eingegebener Standardklasse.
  Mietausfall2/4% Rohertrag. Diese drei zusammen mindestens15% Rohertrag;
  zusätzliche nicht umgelegte Betriebskosten und Modernisierung anschließend.
  Modernisierung je ausdrücklich beurteiltem Risiko: none0/low0.2/medium0.5/high0.75%.
  Schließlich mindestens tatsächliche/kalkulierte Gesamtkosten. Akuter Mietausfall
  ist gesonderter Wertabschlag und wird nicht nochmal als jährliche Kosten gebucht.
  Soll G10000,H100000,gewerblich,medium,none,alle Schätzungen0:100+500+400=1000,
  Floor1500 =>N8500. Extra Betrieb100/Modernisierung500 =>Kosten2100.
- Altersminderung linear=1-RND/GND; RND<=GND; GND nach Anlage2 kontrollieren.
  Andere begründete Modelle bleiben explizite Eingaben im Sachwertbaustein.
  Soll RND30/GND60 =>50%.
- Bauzustandsgrenze=Boden+Fortschritt*min(fertiger Sachwert-Boden,
  fertiger Ertragswert-Boden), anschließend expliziter Nachhaltigkeitsabschlag.
  Nur nichtnegative Gebäudeanteile, Fortschritt0..1; unabhängiger Bautenstandnachweis
  bleibt Pflicht. Soll Boden20, Sach100, Ertrag80, Fortschritt0.5 =>50.
- Verfahrensabgleich: income_standard benötigt Ertragswert plus Sach-/Vergleichs-
  kontrollwert. Kontrollwert<80%Ertrag erzeugt Überprüfungspflicht, nicht automatisch
  einen neuen Mindestwert. Maßgebliche Grenze min(Ertrag,Marktwert) minus noch nicht
  berücksichtigte Abschläge. owner_cost/owner_comparison brauchen eigennutzungs-
  geeigneten Objekttyp, dokumentierte Eignung, ggf.Mietabschlag. SFH/duplex bei
  Vergleichswert>=5 Vergleichsobjekte oder qualifiziertes Modell nach§19(2).
  Nutzer muss bestätigen, dass Abschläge nicht schon enthalten sind. Fehlende
  Nachweise liefern REVIEW_REQUIRED. Festsetzung bleibt externe Entscheidung.
  Soll Einkommen100, Kontrolle70, Markt110, vorgeschlagener Wert95:
  arithmetisch innerhalb100, aber ohne Überprüfungsnachweis REVIEW_REQUIRED.
- Auslands-Ewigkeit N/z nur mit nachgewiesener zusätzlicher Gebäudeabschreibung
  in N und landesspezifischer Methodenbegründung. Equivalent-cap-rate für gleiche
  Zielbewertung mit reduziertem Kostenabzug wird mit dokumentierter Bisektion
  gelöst, auf dem Standardfall der expliziten Kapitalisierungsfunktion; kein
  stilles Weglassen von Kosten. Beide Sichten sind abzustimmen.
- Schiffs-/Flugzeugwert muss auch unter nachhaltig festgesetztem Wert, aktuellem
  Marktwert soweit vorhanden und Methodenobergrenze bleiben. Ein einzelner
  Marktwertminimierer ist keine vollständige Bewertung. Bauteile/Zustand, Wartung,
  Marktdatenvergleich und Langfristannahmen sind Gutachtereingaben mit Nachweis.
- Überwachung: Datum letzte Prüfung plus ein Kalenderjahr (Feb29->Feb28),
  Überprüfung bei materieller Verschlechterung, oder wesentlichem Rückstand>=90T;
  Ausnahme für eigengenutzte Wohnimmobilien nur beim Rückstandsauslöser.
  Soll letzter2024-02-29, Stichtag2025-02-28 =>Überwachung fällig;
  Wohn-Eigennutzung mit90T Rückstand allein löst nicht automatisch Überprüfung aus.

Testtoleranzen wie STARTKERN; Beurteilungen exakt. Getrennte jährliche Kosten,
einmalige Abschläge und doppelte Zuordnung ausdrücklich prüfen.

## Präzisierung nach dem ersten erweiterten Implementierungsblock

Parameterkontrolle: Restnutzungsdauer gegen Anlage2, Mindestzins gegen explizit
gelieferte BaFin-Basis plus Anlagenaufschlag minus beantragtem Prime-Abschlag.
Die Basis muss innerhalb der gesetzlichen Bandbreite liegen. Prime benötigt
alle acht einzeln benannten Kriterien und eine Begründung; fehlende Nachweise
ergeben REVIEW_REQUIRED. Werte über/unter Grenzen ergeben FAILED. Der Testwert
0.055 für Wohnnutzung ist ein synthetischer übergebener Bekanntgabewert, keine
Behauptung eines geprüften aktuellen BaFin-Satzes.

Kleindarlehen: Darlehen+Vorlasten<=600000EUR, gewerblicher Ertragsanteil<=1/3,
inländische Wohnnutzung. Die Besichtigungsalternativen werden separat geprüft:
bekannt/vergleichbar innerhalb2J, bekanntes Fertighaus und Bauplatz, Video mit
RND>=40J, vollständigem Einblick,Dokumentation und>=5%Abschlag, oder nur außen
bei bekannten wesentlichen Parametern und Baualter<=10J bzw.>=10%Abschlag.
Jede Ausnahme braucht dokumentierte Gründe. Die Vergleichbarkeit umfasst
entsprechende Wohnung im selben Haus bzw.gleichartiges Haus derselben Siedlung
und ist ein expliziter geprüfter Input. Die Funktion prüft diese Voraussetzungen,
nicht Gutachterqualifikation oder die spätere Repräsentativität der Stichproben.
Jahresabstände sind vom Anwender kalendergerecht zu ermitteln.

Grenzreferenzen:500000+100000 undErtragsanteil1/3 erfüllen die Zahlenbedingungen;
500001+100000 nicht. Video mitRND40 undAbschlag0.05 erfüllt die Zahlenbedingungen,
RND39 nicht. Produktionsnutzung: Basis0.065 plusAufschlag0.01=>Mindestsatz0.075.
Diese Detailverträge wurden nach den ersten Funktionen ergänzt; die Sollwerte
sind unmittelbar aus den gesetzlichen Grenzen abgeleitet, nicht aus Ausgaben
der Library kopiert.

## Dezimalrundung der CPI-Indexierung

CPI-Eingaben besitzen höchstens 15 signifikante Dezimalstellen. Höhere Präzision
wird ausdrücklich zurückgewiesen. Beide Sprachen berechnen den positiven
Dezimalquotienten exakt und runden kaufmännisch auf volle Euro, ohne Epsilon.
Sollfälle: 275 × 53.1 / 129.8 = 112.5 → 113;
275 × 53.0999999999999 / 129.8 liegt strikt darunter → 112.
Python verwendet rationale Dezimalwerte, R dezimale Ganzzahlarithmetik ohne
Zusatzpaket. Diese Festlegung betrifft nur die CPI-Betragsrundung.
