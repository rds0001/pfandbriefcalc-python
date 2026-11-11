# Eignung, Nachweise und integrierte Anwendung

Vertrag vor Implementierung, M050ff. Quellen: lokaler PfandBG-Text §§4–5,
12–26f, DeckRegV §§8–14; die Nachweisprüfung verwendet M030ff.

## Beträge und Einzelbedingungen

`cover_amount`: Forderung, eingetragener Betrag und geringerer Einlösungsbetrag
begrenzen stets die Anrechnung. Bei HYP/SCH/FLG zusätzlich min(eigenes Recht,
max(0,0.6*Beleihungswert-Vorlast)). Bei gewährleisteten öffentlichen Forderungen
begrenzt der belegte Gewährleistungsbetrag die Anrechnung. Ausfallbehandlung nach
§4(4) unterscheidet dinglich gesicherte, wirksam gewährleistete und ungeschützte
Forderungen. Ein Ausfall des maßgeblichen Gewährleistenden schließt dessen
gewährleistete Deckungsforderung aus. Qualifikation ist eine eigene Prüfung.
Soll: Forderung80,Register75,Einlösung70,Beleihungswert100,Vorlast10,Recht80 =>50.
Unbesicherte ausgefallene Forderung80=>0; dieselbe dinglich gesichert=>50.

`mortgage_terms_check`: zulässige Gebietsgruppe nach §13, Ertragsfähigkeit nach
§16; Bauplätze/Neubauten gesondert. Befristete Rechte: Darlehensende spätestens
zehn Kalenderjahre vor Rechtsende und spätestens am wirtschaftlichen Ende.
Soll: Rechtsende2050-02-28 erlaubt Darlehensende2040-02-28, nicht2040-03-01.
Die Gebietsgruppenzuordnung und rechtliche Vergleichbarkeit sind Nachweisfelder.

`transport_loan_check`: quantitative Prüfung für SCH/FLG. Lebensalter am
Darlehensende höchstens min(20,erwarteteLebensdauer), gleichmäßige oder fallende
Jahrestilgungen; Schlussrate zusätzlich nur beim gleichmäßigen Referenzplan
innerhalb Jahrestilgung*(20-LebensalterAmLaufzeitende). Individuelle Ausnahmen
werden ausdrücklich angegeben und benötigen einen zugehörigen Genehmigungsnachweis.
Tilgungsaufschub<=2Jahre, mit ausdrücklicher Ausnahme<=5. Stundung über die
zulässige Höchstdauer benötigt gesondert Treuhänderzustimmung.
Soll: Alter18,10Jahrestilgung,Schlussrate20=>Grenze;20.01=>Verstoß.
Echte Tilgungsbeträge im Vektor werden zusätzlich mit dem Darlehensbetrag
abgestimmt; Betragsabstimmungstoleranz ausdrücklich1e-8, Entscheidungen über
gesetzliche Grenzbeträge ohne allgemeine Toleranz.

`insurance_check`: HYP mit ausgewähltem zulässigem Betragsmaßstab
(Wiederherstellung, wahrscheinlicherHöchstschaden oder min(Forderung,Zeitwertschaden)).
SCH/FLG:1.1*ausstehendeForderung+vorOderGleichrangigeDrittrechte gemäß Wortlaut
§23/§26c. Ausweis der Rechenkonvention, keine Multiplikation der Drittrechte.
Soll100Forderung+20Drittrechte=>130; Deckung129.99 scheitert.
Risikoabdeckung, Durchsetzbarkeit, Versichereranzeige und ggf.Überleitung der
Versicherungsansprüche bleiben konkrete Pflichtnachweise.

## Abgeleitete Nachweise und Status

Der Pflichtnachweiskatalog wird aus Positionsart und tatsächlichen Merkmalen
abgeleitet, nicht aus einer beliebig leeren vom Nutzer übergebenen Liste.
Gemeinsam: wirksame Forderung, Registrierung/Zuordnung, Ausfallbeurteilung,
Limitklassifikation. Primäre dingliche Sicherheiten zusätzlich Gutachten,
unabhängiger Gutachter, aktueller Wert/Überwachung, Recht/Rang/Allokation und
Versicherung. Öffentliche Forderungen: konkrete zulässige Schuldner-/Garanten-
kategorie und Gewährleistungsumfang. Derivate: separater Rahmenvertrag jeGattung,
Festgeschäft/Sicherungsbeziehung, Insolvenzfestigkeit, Vertragspartner,
unabhängige Marktwerte. Ausland, Teilzuordnung, Refinanzierung, PV-OC,
Liquidität, Altbestand und individuelle Ausnahme erzeugen Zusatzanforderungen.

`analyze_pool` nimmt bereits bewertete einheitliche EUR-Positionsdaten entgegen,
prüft Identitäten/Gattung, stellt ein einziges Positionsuniversum für Deckung,
Limits, Stress und Liquidität her und leitet den Nachweisbedarf daraus ab.
Die Beträge werden aus Rohforderungen/Sicherheiten ermittelt; die für den
qualifizierten Teil berechneten Barwerte sind explizite Inputwerte. Keine stille
proportionale Skalierung eines Gesamtforderungsbarwerts bei abweichender Tranche.
Pfandbrief-Ausschluss bei Eigenbestand nur mit gesondertem Nachweis gemäß§4(5).
Negative Derivatmarktwerte werden unabhängig vom Nachweisstatus berücksichtigt.
Positiver Wert einer nachweislich ungeeigneten Forderung ist nicht anrechenbar;
bei fehlenden Nachweisen werden hypothetische Werte samt INCOMPLETE ausgegeben.

Gesamtstatus: FAILED bei negativer Eignung oder rechnerischer Verletzung;
sonst INCOMPLETE bei offenem/abgelaufenem Nachweis; sonst CHECKS_PASSED.
CHECKS_PASSED bezieht sich auf implementierte Rechen- und Eingabekontrollen,
keine Authentifizierung der Belege und keine bankaufsichtliche Bescheinigung.
