# Kennzahlen, Abstimmung und lokale Exporte

Numerischer Kalkulationsumfang zu PfandBG § 28. Vollständige amtliche
Meldebögen, Einreichungsdateien und Fristenprozesse sind ausgeschlossen.

`pool_metrics` verwendet ausschließlich ein Ergebnis von `analyze_pool`.
Es liefert nominale und barwertige Bestände, Überschüsse, OC-Quoten,
reservierte Überdeckung, verbleibende Deckungsspielräume, Stressfehlbetrag,
Liquiditätsbedarf, Puffer und den ersten Tag des höchsten Liquiditätsbedarfs.
Bei Bedarf null fehlt der Spitzentag; bei Nenner null fehlt die Quote.
Negative Spielräume bleiben negativ. Prüfstatus und Kennzeichnung
hypothetischer Werte werden übernommen.

`aggregate_positions` gruppiert eindeutige Positions-IDs nach ausdrücklich
benannten Textfeldern und summiert ein ausdrücklich benanntes numerisches Feld.
Für ökonomisch getrennte Bestände sind Gattung und Währung in die Gruppierung
aufzunehmen. Die Library errät keine Umrechnungskurse.

`maturity_buckets` verarbeitet einen Bestand gleicher Gattung und Währung.
Die inklusiven Obergrenzen liegen bei 6, 12, 18, 24, 36, 48, 60 und 120
Kalendermonaten; danach folgt das offene Schlussband. Bereits fällige Beträge
liegen im ersten Band und werden zusätzlich gesondert ausgewiesen.
Sollfall zum 31.01.2026: 60 fällig am 31.07. gehören ins erste Band;
40 fällig am 01.08. ins zweite. Monatsgrenzen werden kalendarisch bestimmt.

`weighted_ltv` folgt dem verwendeten Hypothekenauslauf gemäß § 28 Absatz 2
Nummer 3: Zähler ist die verwendete Hypothek einschließlich vorrangiger und
gleichrangiger Belastungen, Nenner der Beleihungswert. Der volle Darlehensbetrag
ist kein Ersatz. Bei mehreren Hypotheken auf demselben Grundstück trägt nur
die mit dem höchsten Auslauf bei; Gewicht ist die Höhe der entsprechenden
berücksichtigten Forderung. Gleich hohe Maxima müssen zuvor eindeutig
konsolidiert werden. Nullgewichte tragen nicht bei.
Soll: Gewicht 60 bei Auslauf 0.5 und Gewicht 40 bei 0.75 → 0.60.
Ersetzt eine weitere Hypothek auf dem ersten Grundstück die Auswahl durch
Gewicht 20 bei 0.6, lautet das Ergebnis (20 × 0.6 + 40 × 0.75)/60 = 0.70.

`reconcile_totals` vergleicht benannte Summen mit
|Ist − Soll| ≤ absolute_tolerance + relative_tolerance × |Soll|.
Vorgaben sind 1e−8 absolut und 1e−12 relativ. Diese Rechentoleranz gilt
nicht für gesetzliche Grenzentscheidungen. Fehlende Schlüssel/Beträge ergeben
INCOMPLETE, keine impliziten Nullwerte.

`export_table` schreibt homogene flache Records als UTF-8-CSV mit Komma,
Anführungszeichen um jedes Feld, Dezimalpunkt und 17 signifikanten Stellen.
Fehlende Werte werden leer, Booleans als true/false exportiert. Ziel muss
explizit sein, Elternverzeichnis bestehen und außerhalb installierter
Paketressourcen liegen. Ohne `overwrite=True/TRUE` wird eine bestehende Datei
nicht ersetzt. Für vollständige verschachtelte Ergebnisse dienen Python
`as_dict()` plus JSON bzw. R `saveRDS`; CSV ist kein amtliches Meldeformat.
