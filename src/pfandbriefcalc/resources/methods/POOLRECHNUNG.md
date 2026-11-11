# Eignung und integrierte Deckungsrechnung

Arbeitsbasis: vom Nutzer akzeptierter lokaler Dokumentationsbestand. PfandBG
§§4,4b,12–26f; PfandBarwertV§§2–6; LCR-VerordnungArt9–12. Keine Meldeformate.
Methoden M040ff. Der konkrete Rechtsbezug ist der im Quellenmanifest erfasste
Textstand; historische Sonderprofile werden ausdrücklich ausgewählt, nie geraten.

## Eignung und externe Evidenz

Jeder Deckungswert hat id,kind,currency,category sowie nominelle Forderung,
Registerzuordnung und niedrigeren Einlösungswert, soweit vorhanden. Alle drei
Beträge müssen explizit sein; der anrechenbare Nennwert überschreitet keinen.
Primärbesicherung HYP/SCH/FLG: zusätzlich eigenes Sicherungsrecht, Beleihungswert,
Vorlasten; reguläre Grenze60%. HYP nur zulässige Belegenheit. Bei befristeten
Immobilienrechten Darlehensende mindestens10JvorRechtsende und innerhalb der
wirtschaftlichen Abschreibungsdauer. Transportobjekte: reguläres Darlehensende
bisEnde20.Lebensjahr oder früheremwirtschaftlichenEnde, Tilgungsbedingungen,
Versicherung und Genehmigungen gesondert kontrollieren.

Die Software authentifiziert keine Gutachten/Rechte. Deshalb aus Art/Gattung
abgeleitete Pflichtnachweise über assess_evidence prüfen: wirksamer Anspruch,
Registereintrag/-zustimmung, gesetzeskonforme Bewertung, wirksames Sicherungsrecht,
Rang, Versicherung, Gebietseignung bzw.öffentlicher Schuldner/Garantie.
Unbekannte Nachweise ergeben INCOMPLETE; nicht erfüllte Voraussetzungen FAILED.
Anrechenbarer Betrag beiINCOMPLETE ist nicht als freigegebeneNull zu behandeln;
Pool weist beide Prüfzustände und hypothetische Rechenwerte getrennt aus.
Ausgefallene unbesicherte/ungewährleistete Werte sowie Werte mit ausgefallenem
maßgeblichem Gewährleistenden nach§4(4) werden nicht angerechnet. Besicherter
Ausfall allein führt nicht zu pauschalemAusschluss, er bleibt Wert-/Überprüfungsanlass.

Weitere Deckungswerte werden explizit einer gesetzlichen Kategorie und deren
Nachweisvertrag zugeordnet. Ein Kreditinstitutsrating ersetzt keinen Nachweis
der Gruppenzugehörigkeit, Gleichwertigkeit oder unbedingten Forderungsqualität.
Derivate laufen proGattung/Rahmenvertrag mit extern unabhängig ermittelten
Marktwerten in Basis und Stress; keine Ableitung eines Optionsmarktwerts durch
gewöhnliche Bond-Diskontierung. Verbindlichkeiten zählen auch bei offenen
Eignungsnachweisen weiter, damit deren Weglassen keine Deckung verbessert.

## Deckungsarithmetik

Nennverbindlichkeit jePfandbrief=max(Nennwert,bekannterMaximal-Einlösungswert).
Nominalerforderlich=Lnom*(1+qnom) plus ausdrücklich bezifferte Zusatzanforderung.
qnom=2%HYP/OEF,5%SCH/FLG für den regulären vorliegenden Textstand.
Basisbarwert erforderlich=Lpv*1.02 plus barwertigeZusatzanforderung.
Pfandbrief- und Derivateverbindlichkeiten jeweils einbeziehen.

OC-Zuordnung ist eine separate Tabelle mit asset_id,role(NOMINAL_OC/PV_OC),
fraction in[0,1]. Summe derFraktionen jephysischemWert<=1. PV_OC nur in dafür
geeigneten Werten; Nominal_OC aus separat belegten Anteilen. Zusätzliche
Pflichtbeträge müssen tatsächlich zugewiesen sein, nicht nur als Gesamtquote
rechnerisch existieren. AlleWerte dürfen den Deckungsgrundbestand unterstützen;
die beiden sicherndenÜberdeckungen haben disjunkte Zuordnungen.

Stresstest nachPfandBarwertV§4–6: jeZinsszenario undWährung Nettobarwert bilden,
danach adversenFX-Abschlag anwenden. Kein gattungsübergreifendesNetting.
Stressanforderung ist A_stress-L_stress>=0 nach§4Abs1Satz1, nicht automatisch
eine zusätzliche2%-Quote in jedemStresstest. HöchsterFehlbetrag=max(0,-minSalden).
Die2%barwertigeOC bleibt gesonderteBasisanforderung. Zusätzliche explizite
aufsichtliche/vertragliche Anforderungen separat ausweisen.

Konkretisierung der Ressourcenbindung vor Implementierung: Für die nominale
Deckung wird der Nennwert des für barwertige OC reservierten Anteils abgezogen.
Der verbleibende Nennwert muss Grunddeckung plus nominale OC tragen. Zusätzlich
müssen die ausdrücklich der nominalen OC zugeordneten Anteile mindestens deren
Pflichtbetrag erreichen; nach beiden Reservierungen muss die nominale
Grunddeckung übrig bleiben. Damit reicht etwa98+2+2 bei einer Verbindlichkeit100
nicht aus, auch wenn die zwei Reservierungen verschiedene Wertpapiere betreffen.
Die reine Barwertquote und die gesonderte Qualifikation der barwertigen OC werden
zusätzlich geprüft. Reservierungen sind explizite Allokationen, kein Optimierer.

Die elementaren Poolfunktionen erhalten qualifizierte Beträge in genau einer
Berichtswährung. Sie stellen keine Eignungserklärung aus. Rohwährungsumrechnung,
Evidenzbeurteilung und Ergebniszusammenführung bleiben nachvollziehbare eigene
Schritte. Grenzprüfungen verwenden Betrag <= Quote*Nenner, keine Division durch0.

SollHYP: Bond100, PV100; Assets100+NomOC2+PVOC2 (alleBasisPV=Nennwert):
nominaleDeckung104gegen102; PV104gegen102; jeweilszugewieseneOC2; ChecksPASS.
Dieselben2Asseteinheiten zugleichNomOCundPVOC=>OVERALLOCATION.
SCH/FLG:100+NomOC5+PVOC2=>107gegen105nominal/102barwertig.
EinZinsstressAktiva98/Passiva100=>zusätzlicherBarwertbedarf2, auchwennBasisPASS.

## Limits

Kumulative Kategorien8%,10%,15%,20% des jeweiligenPfandbriefnennumlaufs nach
§19/§20/§26/§26f. OEF hat keine zusätzliche20%-Ersatzdeckungsgrenze; seine
besondere20%-Grenze für bestimmte herabgestufteDrittstaatforderungen separat.
Freistellungen der barwertigenOC nur für in§4(1)genannteKategorien/Anteile;
reinliquiditätssicherndeWerte entsprechend§4(1a)behandeln. Bankengruppenlimit2%
mitseiner eigenenBezugsmenge; kein pauschalesÜbertragen allerFreistellungen.
HYPBau+Land<=10%allerDeckungswerte,Land<=1%. SCHBauwerke<=20%derverwendeten
Schiffshypotheken. UngeklärtesNicht-EU-VorrechtHYP/OEF<=10%desgeschütztenBestands,
SCH/FLG<=20%; Ersatzdeckungsforderungen nach§20(3)separat prüfen.
Derivatverbindlichkeiten ohne reineFX-Hedges <=12% vonBondPV+entsprechenden
Derivatverbindlichkeiten. KeineSaldierungvonPositiv-/Negativmarktwerten über
rechtlichnichtzusammengehörigeRahmenverträge.
SollBankgruppe2beiBond100=>Grenze;2.01=>Verstoß. HYPungeschützt10/geschützt100
=>Grenze;10.01=>Verstoß. Nicht Nenner110 verwenden.

## Liquidität und Ergebnisse

Genau180Folgetage abStichtag; alleTage einschließlichNulltagen. Eingetragene
Aktiv-,Bond- undDerivatecashflows nachVertragsdatum, keine automatisch
angenommeneFälligkeitsverlängerung. Bedarf aus schlechtestemkumuliertenSaldo.
Puffer aus separatqualifiziertenAssets zuMarktwertnachzutreffendemLCR-Abschlag
oder geeignetenBankguthaben mitRestlaufzeit<=3Kalendermonaten. Keine allgemeine
LCR-Quote undkeine pauschaleÜbernahmevonLCR-Konzentrationskappen inPfandBG§4(1a).
Für denselben durchMonetisierung imPuffer verwendetenWert dürfen keine
inkonsistenten zusätzlichenLiquiditätszuflüsse alsunabhängigeDeckung unterstellt
werden; Monetisierungs-/Cashflowszenario explizitangeben.

Gesamtstatus FAILED beiRechen-/Eignungsverstoß, INCOMPLETE beiunaufgelösten
Pflichtnachweisen, CHECKS_PASSED nurfürdie konkretimplementiertenKontrollen.
AtomareNenn-/Barwerte,OC-Anteile,Limitauslastungen,180Tagesvektor undStresssalden
bleibenimErgebnis. EinPASSistkeineinstitutsbezogeneaufsichtlicheFreigabe.

Toleranzen: Werte1e-8absolut/1e-12relativ, Entscheidungen ohne verstecktes
Wegtolieren vonGrenzverletzungen. Grenzgleichheit zulässig.
