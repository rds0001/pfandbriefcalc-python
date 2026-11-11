# Zahlungsströme und Risiken – konkreter Methodenvertrag

M010–M019, Stand 2026-11-11. Gesetzliche Referenz: lokal gelesene PfandBarwertV
§§2–8, Zeilen 44–128. Anleiheanalysen sind separat gekennzeichnete mathematische
Analysen; keine Behauptung einer gesetzlichen Renditekonvention.

## Kalender und Zahlungsplan

Datum strikt YYYY-MM-DD, keine Zeitzone. Feiertage explizite Datumsmenge,
Wochenende Samstag/Sonntag. Following, modified following, preceding oder
unadjusted. Periodengrenzen bleiben unadjustiert; Zahlungstag wird adjustiert.
Plan rückwärts von Endfälligkeit, Frequenz 1/2/4/12, kurzer Anfangsstub möglich.
Monatstag bleibt an der Endfälligkeit verankert; Monatsende nur ausdrücklich.
Valide Perioden müssen lückenlos aneinander anschließen. Zinstage ACT/365F,
ACT/360, 30E/360 (europäisch, kein ISDA-Februar-Sonderfall), ACT/ACT-ISDA.
Anfang exklusiv/Ende inklusiv als Datumsdifferenz. ACT/ACT teilt an Jahresgrenzen.
Nicht unterstützte Konventionen erzeugen Fehler, keinen Ersatz.

Kupons auf Bestand vor Tilgung mit explizitem Satz pro Periode oder konstantem
Satz; Zins = Bestand * Satz * Tagesbruch. Tilgungsvektor nichtnegativ, keine
Übertilgung. Rest wird am Ende fällig. Gezahlte Zwischenbeträge werden abgezogen.
Ein geliefertes Reset-Szenario kann variable Zinssätze abbilden; keine stille
Prognose, Option oder vorzeitige Tilgung. Marktwert komplexer Derivate ist extern
unabhängig zu liefern (§3); sie dürfen nicht als gewöhnliche feste Anleihe gelten.

Soll: 2024-02-28 bis 2024-03-01 ACT/365F = 2/365, ACT/ACT = 2/366.
2025-01-31 bis 2025-02-28 30E/360 = 28/360. Wochenende 2025-08-31:
following 2025-09-01, modified following 2025-08-29. Zweijährige jährliche
Zahlung, jeweils Tagesbruch 1, Nennwert100, Kupon10%: 10 und110; mit erster
Tilgung40: 50 und66.

## Kurve, Barwert, Rendite und Sensitivität

Kurvenpunkte t>=0 strikt steigend, endliche kontinuierlich verzinste Nullzinsen.
Lineare Interpolation dieser Nullzinsen; Extrapolation nur mit ausdrücklich
gewähltem flat-zero-Modell, sonst Fehler. Keine Umdeutung von Swap-Parsätzen in
Nullzinsen. Diskontierung exp(-z*t). Zahlungsbetrag darf negativ sein, Zeit>=0.
Spread additiv in Dezimaleinheiten. Alle Beträge gleiche Währung; FX separat mit
expliziter Richtung EUR je Fremdwährungseinheit. Grenzfälle/Überlauf ablehnen.

Rendite auf positive Zahlungsbeträge mittels periodischer Verzinsung
P(y)=Sum(C_i*(1+y/m)^(-m*t_i)); y>-m. Bisektion in explizitem Intervall,
kein unerkannter anderer Lösungszweig. Preis>0; mindestens ein positiver
Zahlungsstrom mit t>0. Macaulay-Duration=Sum(t_i PV_i)/P,
modified=Mac/(1+y/m), convexity=Sum(t_i*(t_i+1/m)*PV_i)/P/(1+y/m)^2.
Clean-Preis in Betragseinheiten = Dirty-Preis minus explizite Stückzinsen;
keine implizite Quotierung pro100. Stückzins aus Vertragszinssatz, Bestand und
Daycount seit unadjustiertem Kuponbeginn. Negative Kupons dürfen in Cashflows
stehen; der monotone Yield-Solver nimmt sie nicht an.

Soll: Nullkupon110 in1J, y10%, m1 =>P100, Mac1, modified10/11,
convexity200/121. Kontinuierlicher Nullzins log(1.1) =>PV100.
Zwei Zahlungen10/110 zu1/2J, y10% =>P100. Basiszins0, Zeiten1/3 und
Nullzinsen0/0.04: interpolierter Zweijahreszins0.02 =>100*exp(-0.04).

## Gesetzliche Stressbeträge

Statisch Zins: 250bp, kein Nullzins-Floor. Dynamisch je Kurve mindestens
Stützstellen 1/12,1,2,5,7,10,15J. 250 historische Beobachtungen pro Stützstelle
ergeben249 Tagesänderungen. Nutzer muss Bankarbeitstage und Marktdatenqualität
nachweisen. Standardabweichung: explizit ddof=0 oder1, standardmäßig1; dieselbe
Methode durchgehend, Dokumentation/Genehmigung eines Wechsels bleibt erforderlich.
Bei ausschließlich positiven historischen Zinsen: sd(diff(log(z)))*2.33*sqrt(125)
*aktuellem Zins, mindestens0.01. Enthält eine Stützstelle an einem historischen
Tag null/negativen Zins: gesamte Kurve sd(diff(z))*2.33*sqrt(125), mindestens0.01.
Ausgabe in Dezimalzinseinheiten, nachvollziehbarer Modus. Anschließende
Interpolation ist wie dokumentiert linear in Nullzinsen.

Statische FX-Klassen aus §6(2): EU/EEA/CH10%, US/CA/UK/JP20%, übrige>=25%;
Zuordnung ist expliziter stichtagsbezogener Input. Dynamisch positiver Kursverlauf
mit250Beobachtungen, sd(diff(log(FX)))*2.33*sqrt(125) als relative Änderung.
Keine künstliche Obergrenze der Stressgröße. Netting pro Fremdwährung N=A-L,
adverser EUR-Wert=N*FX-abs(N)*FX*stress. Negative gestresste Kurse werden als
Modellproblem abgelehnt, wenn der Stress eines positiven Nettowerts >100% wäre.

Soll: konstanter positiver Verlauf =>dynamischer Zinsbetrag100bp,
konstanter FX-Verlauf =>0. N=+100/-100, EUR je Einheit0.9, Stress20% =>72/-108.
Statischer Zinsstress auf0.01 =>up0.035/down-0.015. Kein Ausschluss negativer
Zinsen im Down-Szenario. Nichtpositive Historie schaltet alle Stützstellen um.

Rechenergebnisse behalten Modell-, Quellen- und Zwischenwertbezug. Rechtliche
Deckungsabnahme, aktuelle FX-Länderklassifikation, Derivatebewertung und
Methodenfreigaben sind getrennte Anforderungen. Geldtoleranz1e-8, relative1e-12,
Solverrendite1e-12; Entscheidungscodes exakt.
