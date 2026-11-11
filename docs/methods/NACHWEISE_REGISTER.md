# Regelwahl, Nachweise und Register – Implementierungsvertrag

M030–M035. Bitemporale Auswahl ist technische Methodik. Rechtliche Bezugsquellen
für Nachweisinhalte: PfandBG§§2–5,8–11,27,30ff; BelWertV§§5–7,25–26;
SchiffsBelWertV/FlugBelWertV, DeckRegV und RefiRegV. Die vorliegende generische
Auswahl wird durch die abgeleiteten Positions- und Poolpflichten sowie das
lebende Norminventar ergänzt. Sie authentifiziert keine fachlichen Belege.

## Daten- und Fehlervertrag

Listen von Datensätzen; R darf äquivalente data.frames verwenden. Stringschlüssel
nichtleer, keine stillen Dubletten. Datum YYYY-MM-DD; Intervalle einschließlich
beider Grenzen. Keine NA/NaN/Inf oder logischen Werte als Zahlen. Quellverweis,
verantwortlicher Prüfer und Begründung sind nichtleere Texte; deren Echtheit
bleibt extern. Eingaben werden nicht verändert.

## Regelprofile

Jede Revision enthält profile_id,revision,valid_from,valid_to,known_from,
status(VERIFIED/EXPERIMENTAL),source_ref,parameters. Proprofile_id zuerst die
neueste bekannte Revision wählen, dann deren Geltungsintervall prüfen. Damit
reaktiviert eine korrigierte Geltungsdauer keine zurückgezogene alte Revision.
Gleicher Wissenszeitpunkt mit konkurrierenden Revisionen ist mehrdeutig und ein
Fehler. Keine Defaultfassung, kein Fallback auf fachlich ungeprüfte Profile.
Auswahl eines experimentellen Profils nur explizit allow_experimental=True.
Ergebnis trägt ausgewählte Revision, Wissens-/Geltungsstichtag und Parameter.

Soll synthetisch: RevisionA gültig2025, bekannt2024-12-01, Quote0.02;
RevisionB korrigiert dieselbe Geltung, bekannt2025-06-01, Quote0.03.
As-of2025-03-31/known2025-04-01=>A; known2025-07-01=>B.
Wird beiB die Geltung auf2025-07-01 verschoben, ist fürAs-ofMärz beiWissensstand
Juli keine Revision gültig; A darf nicht still reaktiviert werden.

## Nachweise

Anforderungsliste enthält requirement_id,scope,allow_not_applicable,source_ref.
Evidenzrevision enthält evidence_id,requirement_id,scope,valid_from,valid_to,
known_from,conclusion(MET/NOT_MET/NOT_APPLICABLE),reviewer,source_ref,reason.
Je evidence_id neueste bekannte Revision; für eine Anforderung müssen alle
gültigen Evidenzen widerspruchsfrei sein. Eine zulässige Nichtanwendbarkeit
benötigt ausdrückliche Begründung und erlaubende Anforderung.
Fehlend, abgelaufen, zukünftige Geltung und nicht erfüllt separat ausweisen.
AggregatFAILED beiNOT_MET oder unerlaubterN/A, INCOMPLETE bei offenen Nachweisen,
sonstCHECKS_PASSED. Mehrdeutigkeit oder unpassende Schlüssel erzeugen Eingabefehler.

Soll: eineAnforderung/keineEvidenz=>INCOMPLETE/MISSING; gültigerMET-Beleg=>PASS;
Datumnachvalid_to=>INCOMPLETE/EXPIRED; gültigerNOT_MET=>FAILED. Eine neue später
bekannteNOT_MET-Revision darf einen früheren As-known-Lauf nicht ändern.

## Mengenallokation und Registerereignisse

Explizite Knotenlimits für Forderungen und Sicherheiten; Allokationskanten mit
eindeutiger allocation_id,claim_id,collateral_id,kind,currency,amount. Summen pro
Forderung/Sicherheit dürfen deren Kapazität nicht überschreiten. Alle Beträge
proverbundenerKante gleicheWährung; kein gattungsübergreifender Ausgleich.
Die Kapazität der Sicherheit ist bereits nach Rang/Vorlasten qualifiziert.
Kein automatischer Optimierer, keine Rangentscheidung aus Datensatzreihenfolge.
Soll Forderungen60/50, Sicherheit100, Zuordnungen60/50=>OVERALLOCATION.
Zuordnungen60/40=>100, beideKnotengrenzen eingehalten.

Registerevents: event_id,asset_id,kind,effective_date,recorded_at,action(ADD/UPDATE/
REMOVE),payload,reason,evidence_ref. Ereignisse werden nach Wirksamkeit geordnet,
gleichen Tags explizite ganzzahlige sequence. Nur biszumWissensstichtag bekannte
Ereignisse berücksichtigen. UPDATE/REMOVE benötigen vorhandenen aktivenEintrag,
ADD darf keinen aktivenEintrag überschreiben; Gattung einesEintrags unveränderbar.
Ergebnis enthält aktiveEinträge und angewandteEventIDs; Originalhistorie bleibt
unverändert. Keine produktive Registerführung und keine rechtliche Wirksamkeit
allein aufgrund eines technisch gültigen Ereignisses.

Soll ADD100amJan1, UPDATE90amFeb1erstbekanntMärz1: Feb15knownFeb15=>100;
Feb15knownMärz2=>90. REMOVEohneADD oder zweiaktiveADD=>Fehler.
