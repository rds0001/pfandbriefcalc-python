# Registerdaten und Abwicklungsszenarien

Quellen: DeckRegV §§ 8–14 und 18; PfandBG § 30 Absätze 2a, 2b und 7.

`validate_register_entries` prüft geplante Neueinträge gegen alle bisher
verwendeten Nummern, einschließlich gelöschter Einträge. Gattung, Register
und Nummer bilden den eindeutigen Schlüssel. Nummern sind positive ganze
Zahlen oberhalb der bisher höchsten Nummer. Eintragsdatum und tatsächliches
Erfassungsdatum müssen übereinstimmen; Rückdatierung wird abgelehnt.
Analytische Wissenskorrekturen sind davon getrennte Registerereignisse.

Die aktuellen Feldverträge gelten für Einträge ab 01.07.2023. Frühere Einträge
benötigen ausdrücklich `legacy_fields` und `legacy_source_ref`. Kategorie-
und Zusatzfelder ergeben sich aus dem Datenvertrag: insbesondere Garantie,
Refinanzierung, Treuhand, Teilforderungen, Versicherung und Derivate.
Fehlende Felder ergeben INCOMPLETE; Nummernwiederverwendung oder Rückdatierung
FAILED. Die Library authentifiziert den Inhalt nicht und betreibt kein Register.

`deferred_interest` berechnet Betrag × vereinbarter Coupon × expliziten
Jahrbruch. Der Zinssatz wird nicht geraten. Negative Coupons dürfen den
fortgeschriebenen Betrag nicht unter null drücken.

`interest_extension` bildet die besondere Verschiebung eines ursprünglichen
Zinszahlungstermins innerhalb des ersten Monats nach Sachwalterbestellung ab.
Der neue Termin ist das Ende dieses Kalendermonatszeitraums; Entscheidung muss
innerhalb des zulässigen Zeitraums liegen. Auf den verschobenen Betrag fallen
vertragliche Zinsen an, die zum Kapitalbetrag werden. Die Berechtigung ist
ein externer Status, kein automatisch bejahter Softwarebefund.

`extension_plan` behandelt eine ausdrückliche Kapitalverschiebung je Emission:
ursprüngliche Fälligkeit, neuer Termin, Kapital, einheitlicher verschobener
Anteil, Coupon und Daycount. Der neue Termin liegt höchstens zwölf
Kalendermonate nach dem ursprünglichen. Die Entscheidung erfolgt nicht nach
der ursprünglichen Fälligkeit. Emissionen derselben Gattung sind vollständig
zu erfassen; dies wird durch einen ausdrücklichen Vollständigkeitsnachweis
angebunden. Jeder verschobene Anteil erhält denselben Termin je Emission.

Zu jedem Zahlungstermin darf eine ursprünglich später fällige Emission nicht
zu einem höheren Anteil getilgt sein als eine ursprünglich früher fällige,
noch nicht vollständig getilgte Emission. Voraussetzungen nach § 30 Absatz 2b
werden nur für Verschiebungen innerhalb des ersten Monats nach Bestellung
als gesetzlich vermutet behandelt; darüber hinaus sind sie explizit nachzuweisen.
Derivate sind nicht Teil dieser Verschiebungsbefugnis.

Die Funktion verändert den vertraglichen Basisplan nicht. Ihr Modell besitzt
höchstens zwei Kapitalzahlungstermine je Emission: unverschobener und
verschobener Anteil. Besondere Zinsinteraktionen, abweichende Verträge und
umfassendere Pläne müssen in der vollständigen externen Szenarioqualifikation
berücksichtigt werden. Das Ergebnis ist ein prüfbarer Kalkulationsplan und
keine rechtswirksame Entscheidung des Sachwalters.
