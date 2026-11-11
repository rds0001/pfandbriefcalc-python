# Fachvertrag des ersten nativen Durchlaufs

Status: SPECIFIED für die hier genannten Methoden, keine Gesamtfreigabe.
Quellen: lokale nummerierte amtliche Browsertexte in `quellen/texte/`.
Der Dokumentationsbestand wurde als Arbeitsgrundlage akzeptiert. Beschaffungsformat,
Fassung und fachliche Prüftiefe bleiben im Quellenregister getrennt ausgewiesen.

## M001 – Vervielfältiger

BelWertV § 12 Absatz 1, lokale Zeile 159. V = (1-(1+z)^(-n))/z.
z ist ein positiver expliziter Jahreszinssatz, n eine nichtnegative endliche
Restnutzungsdauer in Jahren. Der mathematische Grenzfall z=0 ergibt n; er ist
keine Freigabe eines regulatorischen Kapitalisierungszinssatzes von null.
Stabile Auswertung über log1p/expm1. Unendliche Nutzungsdauer benötigt einen
eigenen Auslandsvertrag und gehört nicht in diesen Startfall.

Unabhängiger Sollfall: z=0,10, n=2: 1/1,1 + 1/1,21 = 210/121.
Numerische Toleranz absolut 1e-12, relativ 1e-12 (dimensionslos).

## M002 – Ertragswert und besondere Fälle

BelWertV §§ 8–13. Expliziter bereits fachlich ermittelter Jahresreinertrag N,
Bodenwert B, Kapitalisierung z>0, Restnutzungsdauer n. Keine versteckte aktuelle
BaFin-Zinsannahme. Standardfall B+(N-zB)*V, sofern n>=30 und N-zB>0.
Bei n<30 muss der Nutzer die zulässige Alternative ausdrücklich wählen:
`capitalize_land`: N*V; `deduct_demolition`: Standardwert minus abgezinsten
Abbruchkosten. Bei N-zB<=0 gilt ausschließlich der um Abbruchkosten verminderte,
bis zur Verfügbarkeit des unbebauten Grundstücks abgezinste Bodenwert. Dieser
Zeitpunkt ist explizit zu übergeben. Negative Ergebnisse bleiben sichtbar und
werden nicht als positive beliehbare Werte freigegeben. Hoher Bodenwertanteil
erzeugt einen Nachweishinweis, keine automatische fachliche Begründung.

Sollfall für n=2, z=0,10, N=100, B=200, Alternative capitalize_land:
21000/121. Fall ohne Gebäudeertrag: N=10, B=200, Abbruch=20,
Verfügbarkeit nach 2 Jahren: 18000/121.

## M003 – Vergleichswert und M004 – Sachwertbaustein

BelWertV § 19: expliziter nachhaltig abgeleiteter Ausgangsvergleichswert und
Sicherheitsabschlag >=0,10, <1; kein Ersatz für Vergleichseignungsnachweise.
Sollfall 100000 und 0,10 ergibt 90000.

BelWertV §§ 14, 16, 17: Herstellungswert H, Abschlag h>=0,10,
Baunebenkostenquote b zwischen 0 und 0,20 auf H*(1-h), explizite Alterswert-
minderung a zwischen 0 und 1; linearer Spezialfall a=1-RND/GND. Gebäudeanteil
H*(1-h)*(1+b)*(1-a). Boden wird separat addiert; weitere Abschläge und
gegebenenfalls abgezinste Abbruchkosten werden explizit abgezogen. Auswahl einer
anderen zulässigen Alterskurve ist ein dokumentierter externer Modellparameter.
Sollfall H=100000, h=0,10, b=0,20, a=0,25: Gebäudeanteil 81000.

## M005/M006 – Schiff-/Flugzeugwertobergrenze

SchiffsBelWertV § 4 und FlugBelWertV § 4: Obergrenze ist nicht Wertfestsetzung.
Schiff: min(aktueller Marktwert nach Historienabschlag, historischer Durchschnitt,
Neubau-/Kaufpreis). Unter zehn verfügbaren Jahren Abschlag 0,15; bei höchstens
drei Jahren mindestens 0,25. Fehlender aktueller oder durchschnittlicher Marktwert:
anderes angemessenes Verfahren mit Obergrenze 0,75*Neubau-/Kaufpreis; dessen
Methodennachweis bleibt erforderlich. Ein optional höherer Abschlag ist explizit.
Historienjahre sind ganze Kalenderjahre, Durchschnitt ist explizit ermittelt.

Flugzeug: min(aktueller Marktwert, Zehnjahresdurchschnitt, ausgeglichener Wert).
Kürzere/fehlende Historie: ausgeglichener Wert *0,90; vorhandene übrige Grenzen
bleiben bestehen. Fehlender aktueller Marktwert: alternative Bewertung, Obergrenze
0,75*ausgeglichener Wert; ein vorhandener Durchschnitt und die zusätzliche
Historiengrenze bleiben konservativ separat ausgewiesen.

Schiff Sollwerte: Markt=100, Durchschnitt=90, Kauf=110: zehn Jahre 90;
fünf Jahre 85; drei Jahre 75; ohne Markt 82,5.
Flugzeug: Markt=100, Durchschnitt=95, ausgeglichen=110: zehn Jahre 95;
fünf Jahre min(100,95,99)=95; ohne Historie 99; ohne Markt höchstens 82,5.

## M007 – Anrechnungsarithmetik

PfandBG § 14; entsprechender Prozentsatz für Schiff/Flugzeug vor Einbindung anhand
der jeweiligen Vorschriften prüfen. Für bereits separat geprüfte Eignung und
eindeutigen Rang: min(Forderung, eigenes Sicherungsrecht, zugeordneter Betrag,
max(0, Beleihungswert*Grenze - vorrangige Belastungen)). Die Funktion berechnet
nur den zugewiesenen Rangabschnitt, keine rechtliche Eignung oder vollständige
Mehrfachallokation. Alle Beträge in derselben Währung, Grenze explizit.
Sollfall claim=80, lien=100, lending_value=100, prior_claims=20,
assigned_amount=100, lending_limit=0,60: anrechenbar 40.

## M008 – Aggregierte Deckungsarithmetik

PfandBG § 4. Alle Beträge sind bereits separat qualifiziert/zugeordnet.
Nominale Pflicht: Verbindlichkeiten*(1+nominale Quote). Barwertpflicht:
Barwertverbindlichkeiten*(1+Barwertquote). Beide zusätzlichen Beträge benötigen
geeignete getrennte Zuordnungen; für barwertige sichernde Überdeckung verwendete
Werte dürfen nicht die nennwertige sichernde Überdeckung erfüllen.
Getrennte Nachweise aus Inputtabellen und eine Einheitenprüfung bleiben für den
späteren Gesamtlauf erforderlich. Der Starthelfer ist ausdrücklich nur Arithmetik.
Sollfall Verbindlichkeiten=100, Assets=103, Quote=0,02: Pflicht 102, Headroom 1.

## M009 – Taggenaue Liquiditätslücke

PfandBG § 4 Absatz 1a. Explizite gleich lange tägliche Zufluss-/Abflussvektoren.
Kumuliertes Saldo bis zu jedem Tag; Bedarf=max(0,-min(kumulierte Salden)).
Der regulatorische Aufrufer muss den vollständigen erforderlichen Horizont,
Eignung/Bewertung des Puffers und Cashflowvollständigkeit prüfen. Keine
Saldierung allein auf Endsumme. Sollfall Zuflüsse=[0,100], Abflüsse=[50,0]:
Bedarf 50 trotz positivem Endsaldo 50.

## Gemeinsame Fehler-/Ergebnissemantik

Native Python/R-Implementierungen liefern CalcResult mit Wert, Methode,
Quellenbezug, Zwischenergebnissen und Prüfgrenze. Nicht numerische Werte, boolesche
Werte als Zahlen, NaN/Inf und unzulässige Bereiche werden abgelehnt. R recycelt
keine ungleichen Vektoren. Numerische Startfälle mit atol=rtol=1e-12; Geldfälle
mit atol=1e-8 Währungseinheiten, rtol=1e-12. Decisions und Fehlercodes exakt.
Keine Behauptung vollständiger Deckungs- oder Gutachtenfreigabe durch diese Helfer.
