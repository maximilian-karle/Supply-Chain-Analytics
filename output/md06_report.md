# MD06 Ausnahmemeldungsanalyse -- ELA

**Auswertungsdatum:** 01.07.2026  
**Scope:** MRP-Controller 211, 212, 415, 416  
**Analyseebene:** Materialnummer (dedupliziert)  
**Quelle:** SAP MD06-Export (nach MRP-Lauf)  
**Verwendung:** Baseline-Analyse vor SAP PP/DS-Einfuehrung

---

## Methodische Vorbemerkung

SAP MD06 wird im untersuchten Unternehmen nicht aktiv durch Disponenten genutzt.
Der Bearbeitungsstatus (XOO/OOX) ist daher **kein zuverlaessiger Indikator**
fuer Planungsaktivitaet: OOX bedeutet lediglich, dass SAP dieselbe Ausnahme
beim naechsten MRP-Lauf wiedererkannt und automatisch als 'bekannt' markiert hat --
nicht dass ein Disponent aktiv reagiert hat.

**Thesis-relevante Kernaussage:** Alle Materialien im MD06-Export tragen
mindestens eine unbehandelte Ausnahmemeldung. Die relevante Frage ist nicht
XOO vs. OOX, sondern: Wie viele Materialien haben Ausnahmemeldungen,
welche Gruppen dominieren, und wie kritisch ist die Bestandssituation?

---

## 1. Uebersicht -- Materialien mit Ausnahmemeldungen

| MRP-Controller | Materialien mit Ausnahmen | Negativbestand (%) | Bestand <= 0 Tage (%) |
|---|---|---|---|
| 211 | 1,167 | 0.2% | 0.7% |
| 212 | 4,738 | 2.0% | 2.2% |
| 415 | 75 | 2.7% | 4.0% |
| 416 | 36 | 33.3% | 33.3% |
| **Gesamt** | **6,016** | **1.9%** | **2.1%** |

> Hinweis: Alle aufgefuehrten Materialien haben mindestens eine Ausnahmemeldung.
> Materialien ohne jegliche Ausnahme erscheinen nicht im MD06-Export.

---

## 2. Bestandsreichweite (alle Ausnahmematerialien)

| MRP-Controller | Materialien | Median Reichweite (Tage) | Minimum (Tage) | Negativbestand |
|---|---|---|---|---|
| 211 | 1,167 | 9999.0 | -149.0 | 2 (0.2%) |
| 212 | 4,738 | 9999.0 | -246.0 | 96 (2.0%) |
| 415 | 75 | 593.0 | -156.0 | 2 (2.7%) |
| 416 | 36 | 15.0 | -28.0 | 12 (33.3%) |

---

## 3. Ausnahmengruppen-Verteilung

> Gruppenpriorität nach SAP-Standard: Gr.8 (Planungsabbruch) > Gr.5 (StLi-Fehler) > Gr.1-3 (Terminueberschreitung) > Gr.7 (Umterminierung) > Gr.6 (Bestand) > Gr.4 (informativ)

### MRP-Controller 211

| Gruppe | Beschreibung | Materialien |
|---|---|---|
| 3 | Endtermin in Vergangenheit | 6 |
| 4 | Allgemeine Meldungen (informativ) | 65 |
| 6 | Verfuegbarkeitspruefung / Bestandsabweichung | 19 |
| 7 | Umterminierung erforderlich | 46 |
| 8 | Planungsabbruch (kritisch) | 6 |

### MRP-Controller 212

| Gruppe | Beschreibung | Materialien |
|---|---|---|
| 1 | Eroeffnungstermin in Vergangenheit | 2 |
| 2 | Starttermin in Vergangenheit | 4 |
| 3 | Endtermin in Vergangenheit | 36 |
| 4 | Allgemeine Meldungen (informativ) | 343 |
| 6 | Verfuegbarkeitspruefung / Bestandsabweichung | 56 |
| 7 | Umterminierung erforderlich | 286 |

### MRP-Controller 415

| Gruppe | Beschreibung | Materialien |
|---|---|---|
| 3 | Endtermin in Vergangenheit | 6 |
| 4 | Allgemeine Meldungen (informativ) | 39 |
| 6 | Verfuegbarkeitspruefung / Bestandsabweichung | 9 |
| 7 | Umterminierung erforderlich | 36 |

### MRP-Controller 416

| Gruppe | Beschreibung | Materialien |
|---|---|---|
| 3 | Endtermin in Vergangenheit | 1 |
| 4 | Allgemeine Meldungen (informativ) | 26 |
| 6 | Verfuegbarkeitspruefung / Bestandsabweichung | 6 |
| 7 | Umterminierung erforderlich | 19 |

---

## 4. ABC-Verteilung der Ausnahmematerialien

| MRP-Controller | A-Teile | B-Teile | C-Teile | Kein ABC |
|---|---|---|---|---|
| 211 | 54 | 81 | 217 | 815 |
| 212 | 358 | 596 | 1130 | 2654 |
| 415 | 45 | 14 | 14 | 2 |
| 416 | 16 | 4 | 1 | 15 |

---

## 5. Bearbeitungsstatus -- nur zur Referenz

> **Achtung:** XOO/OOX ist bei diesem Unternehmen kein Indikator fuer Planungsaktivitaet.
> OOX wird von SAP automatisch gesetzt, wenn dieselbe Ausnahme MRP-laufuebergreifend fortbesteht.

| MRP-Controller | XOO (unquittiert) | OXO (Reichweite) | OOX (auto-quittiert) |
|---|---|---|---|
| 211 | 8 (0.7%) | 0 (0.0%) | 1159 (99.3%) |
| 212 | 96 (2.0%) | 7 (0.1%) | 4635 (97.8%) |
| 415 | 2 (2.7%) | 1 (1.3%) | 72 (96.0%) |
| 416 | 12 (33.3%) | 0 (0.0%) | 24 (66.7%) |

---

## 6. Kernbefunde fuer Kapitel 3.3

- **6,016 Materialien** im Scope der vier MRP-Controller tragen Ausnahmemeldungen.
- **1.9%** dieser Materialien (112) haben negativen Bestandsdeckungsgrad -- aktive Unterdeckung.
- Ausnahmengruppe 4 (allgemeine, informative Meldungen) und Gruppe 7 (Umterminierung) dominieren quantitativ.
- Gruppe 8 (Planungsabbruch) und Gruppe 5 (Stuecklistenfehler) sind qualitativ kritischer -- Einzelfaelle pruefen.
- Die fehlende aktive Nutzung von MD06 bestaetigt das Planungsdefizit: Ausnahmemeldungen laufen systematisch ins Leere.
- Diese Ausgangssituation begruendet den Einsatz von SAP PP/DS Alert Management als strukturierte Eskalationslogik.

---

*Erstellt: 01.07.2026 | Anonymisiertes Industrieprojekt (ELA) | Masterarbeit WI -- MCI 2026*