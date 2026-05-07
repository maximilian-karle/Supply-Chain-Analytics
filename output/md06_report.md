# MD06 Ausnahmemeldungsanalyse -- Erhardt+Leimer GmbH

**Auswertungsdatum:** 07.05.2026  
**Scope:** Disponenten 211, 212, 415, 416  
**Analyseebene:** Materialnummer (dedupliziert -- schlimmster Status je Material)  
**Quelle:** SAP MD06-Export  
**Verwendung:** Kapitel 3.3 -- Ist-Analyse Planungsqualitat

---

## Statuscode-Legende

| Code | Bedeutung | Handlungsbedarf |
|---|---|---|
| **XOO** | Ausnahmemeldung vorhanden -- nicht bearbeitet | **Ja** |
| **OXO** | Bestandsreichweiten-Alarm -- keine Ausnahme | Ja (Reichweite) |
| **OOX** | Ausnahmemeldung bearbeitet/bestatigt | Nein |

> Drei-Zeichen-Ampelsystem: Position 1 = Ausnahmengruppen-Alarm | Position 2 = Reichweiten-Alarm | Position 3 = Bearbeitet

---

## 1. Ubersicht -- Ausnahmemeldungsquoten (Materialebene)

| Disponent | Materialien | XOO (%) | OXO (%) | OOX (%) |
|---|---|---|---|---|
| 211 | 1,167 | **0.7%** | 0.0% | 99.3% |
| 212 | 4,738 | **2.0%** | 0.1% | 97.8% |
| 415 | 75 | **2.7%** | 1.3% | 96.0% |
| 416 | 36 | **33.3%** | 0.0% | 66.7% |
| **Gesamt** | **6,016** | **2.0%** | **0.1%** | **97.9%** |

---

## 2. Bestandsreichweite (XOO-Materialien)

| Disponent | XOO-Materialien | Median (Tage) | Minimum (Tage) | Negativbestand |
|---|---|---|---|---|
| 211 | 8 | 0.0 | -149.0 | 25.0% |
| 212 | 96 | -8.0 | -246.0 | 100.0% |
| 415 | 2 | -81.0 | -156.0 | 100.0% |
| 416 | 12 | -14.5 | -28.0 | 100.0% |

---

## 3. Detailauswertung je Disponent

### Disponent 211

- **Materialien gesamt:** 1,167
- **XOO (unbearbeitet):** 8 (0.7%)
- **OXO (Reichweiten-Alarm):** 0 (0.0%)
- **OOX (bearbeitet):** 1,159 (99.3%)
- **Negativbestand (XOO):** 2 Materialien (25.0%)
- **ABC-Verteilung (XOO):** : 6 | B: 1 | C: 1
- **Ausnahmengruppen:** Gruppe 3: 6 | Gruppe 4: 65 | Gruppe 6: 19 | Gruppe 7: 46 | Gruppe 8: 6

### Disponent 212

- **Materialien gesamt:** 4,738
- **XOO (unbearbeitet):** 96 (2.0%)
- **OXO (Reichweiten-Alarm):** 7 (0.1%)
- **OOX (bearbeitet):** 4,635 (97.8%)
- **Negativbestand (XOO):** 96 Materialien (100.0%)
- **ABC-Verteilung (XOO):** : 15 | A: 45 | B: 21 | C: 15
- **Ausnahmengruppen:** Gruppe 1: 2 | Gruppe 2: 4 | Gruppe 3: 36 | Gruppe 4: 343 | Gruppe 6: 56 | Gruppe 7: 286

### Disponent 415

- **Materialien gesamt:** 75
- **XOO (unbearbeitet):** 2 (2.7%)
- **OXO (Reichweiten-Alarm):** 1 (1.3%)
- **OOX (bearbeitet):** 72 (96.0%)
- **Negativbestand (XOO):** 2 Materialien (100.0%)
- **ABC-Verteilung (XOO):** A: 2
- **Ausnahmengruppen:** Gruppe 3: 6 | Gruppe 4: 39 | Gruppe 6: 9 | Gruppe 7: 36

### Disponent 416

- **Materialien gesamt:** 36
- **XOO (unbearbeitet):** 12 (33.3%)
- **OXO (Reichweiten-Alarm):** 0 (0.0%)
- **OOX (bearbeitet):** 24 (66.7%)
- **Negativbestand (XOO):** 12 Materialien (100.0%)
- **ABC-Verteilung (XOO):** : 3 | A: 6 | B: 2 | C: 1
- **Ausnahmengruppen:** Gruppe 3: 1 | Gruppe 4: 26 | Gruppe 6: 6 | Gruppe 7: 19

---

## 4. Kernbefunde fur Kapitel 3.3

- **Gesamtquote unbearbeiteter Ausnahmemeldungen (XOO):** 2.0% (118 von 6,016 Materialien im Scope)
- **Zusatzlicher Reichweiten-Alarm (OXO):** 8 Materialien (0.1%) -- Bestandsreichweite kritisch, keine formale Ausnahmemeldung
- Die XOO-Quote dient als Baseline-KPI fur die Evaluation in Kapitel 5: Eine Reduktion nach PP/DS-Einfuhrung ware ein messbarer Wirksamkeitsnachweis.
- Disponent 212 (Stellantriebe, Pilotarbeitsplatz AG9) ist mit 4,738 Materialien der volumenstarkste Disponent im Scope.

---

*Erstellt: 07.05.2026 | Autor: Maximilian Karle | Masterarbeit WI -- MCI 2026*