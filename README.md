# Supply-Chain-Analytics

**Baseline analytics for a SAP PP/DS implementation at an automation technology manufacturer.**

This repository documents the pre-implementation diagnostic work conducted as part of a Master's thesis in Industrial Engineering (Wirtschaftsingenieurwesen) at MCI Innsbruck, 2026.

---

## Context

The case company operates a **hybrid MTS/ETO production environment** — standard actuator components (Make-to-Stock) feed into custom web-guiding systems (Engineer-to-Order). Before introducing SAP PP/DS as a finite scheduling and pegging tool, a structured baseline analysis was conducted to quantify the current planning deficit.

The key question: **How many materials already carry unprocessed exception messages — and what does that tell us about planning quality?**

---

## Project Structure

```
erl-supply-chain-analytics/
├── src/
│   └── analyse_md06.py       # Core analysis script
├── output/
│   ├── md06_report.md        # Human-readable Markdown report
│   └── md06_summary.csv      # Machine-readable KPI table (Power BI input)
├── data/                     # Raw exports go here (not tracked in git — see .gitignore)
└── README.md
```

---

## What the Analysis Covers

| KPI | Description |
|---|---|
| Exception rate (XOO) | Share of materials with at least one unprocessed MRP exception |
| Processed rate (OOX) | Share of materials with exceptions that were acknowledged |
| No-exception rate | Share of materials with clean planning status |
| Stock coverage (days) | Median and minimum days of coverage for exception materials |
| Negative coverage share | Share of materials in active understock |
| ABC distribution | Whether exception materials are A/B/C classified |
| Exception group breakdown | Which SAP exception types (groups 1–8) dominate |

---

## Setup

```bash
# Install dependencies
pip install pandas openpyxl

# Configure file paths in src/analyse_md06.py (CONFIGURATION section)
# Then run:
python src/analyse_md06.py
```

Output files are written to `output/`.

---

## Data Privacy

Raw SAP exports are **not included** in this repository (`.gitignore`). All findings reported here use aggregated, anonymised KPIs. No individual order numbers, customer names, or personal data are published.

---

## Thesis Reference

Karle, M. (2026). *Konzeption eines Prozessmodells zur Synchronisation von Serien- und Einzelfertigung durch computergestützte Feinplanung: Integration von Pegging-Beziehungen mittels SAP PP/DS.* Master's thesis, MCI — The Entrepreneurial School, Innsbruck.

---

## Next Steps

- [ ] Power BI dashboard from `md06_summary.csv`
- [ ] Post-implementation comparison (after PP/DS go-live)
- [ ] FA volume trend analysis from COOIS export
