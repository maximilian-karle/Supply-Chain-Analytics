# Supply-Chain-Analytics

**Baseline analytics for a SAP PP/DS implementation at an automation technology manufacturer.**

This repository documents the pre-implementation diagnostic work conducted as part of a Master's thesis in Industrial Engineering (Wirtschaftsingenieurwesen) at MCI Innsbruck, 2026.

---

## Context

The case company operates a **hybrid MTS/ETO production environment** — standard actuator components (Make-to-Stock) feed into custom web-guiding systems (Engineer-to-Order). Before introducing SAP PP/DS as a finite scheduling and pegging tool, a structured baseline analysis was conducted to quantify the current planning deficit and production order volume.

Two questions drive this baseline:

1. **How many materials already carry unprocessed exception messages — and what does that tell us about planning quality?**
2. **What is the actual production order volume, and how is it split between MTS and ETO?**

---

## Project Structure

```
Supply-Chain-Analytics/
├── src/
│   ├── analyse_md06.py       # MD06 exception message analysis
│   └── analyse_coois.py      # COOIS production order volume analysis
├── output/
│   ├── md06_report.md        # Human-readable Markdown report (MD06)
│   ├── md06_summary.csv      # Machine-readable KPI table (Power BI input)
│   ├── coois_report.md       # Human-readable Markdown report (COOIS)
│   └── coois_summary.csv     # Machine-readable KPI table (Power BI input)
├── data/                     # Raw exports go here (not tracked in git — see .gitignore)
└── README.md
```

Both scripts are run from the repository root and follow the same relative-path convention for `data/` and `output/`.

---

## Analysis 1 — MD06 Exception Messages

**Script:** `src/analyse_md06.py`
**Input:** SAP MD06 exports per MRP controller (`data/MD06_Ausnahmemeldungen_<Disponent>.xlsx`)

| KPI | Description |
|---|---|
| Exception rate (XOO) | Share of materials with at least one unprocessed MRP exception |
| Processed rate (OOX) | Share of materials with exceptions that were acknowledged |
| No-exception rate | Share of materials with clean planning status |
| Stock coverage (days) | Median and minimum days of coverage for exception materials |
| Negative coverage share | Share of materials in active understock |
| ABC distribution | Whether exception materials are A/B/C classified |
| Exception group breakdown | Which SAP exception types (groups 1–8) dominate |

### Key Findings

- **6,016 materials** across the four MRP controllers in scope (211, 212, 415, 416) carry at least one active exception message.
- **Controller 212** (actuator line, PP/DS pilot scope): 100% negative stock coverage among unprocessed exception materials, median coverage **-8 days** (minimum -246 days).
- **Controller 416**: 33.3% unprocessed exception rate (12 of 36 materials), flagged as a structural backlog outlier.
- Exception messages are **not actively processed** by any planner in day-to-day operations — direct empirical evidence for the information asymmetry addressed in the thesis.

---

## Analysis 2 — COOIS Production Order Volume

**Script:** `src/analyse_coois.py`
**Input:** SAP COOIS export, plant 1000, calendar year 2025 (`data/FA_2025.xlsx`)

| KPI | Description |
|---|---|
| Total order volume | Total production orders for the analysis year |
| Productive order share | Share of orders classified as MTS (ZP01) or ETO (ZP02) |
| Orders per working day | Average productive orders per working day |
| Order type split | Breakdown by order type (ZP01 / ZP02 / ZP03 / ZP04) |
| MRP controller ranking | Top 15 controllers by productive order volume |
| Pilot scope analysis | Volume share of the four controllers in the PP/DS rollout scope |
| Monthly distribution | Order volume by month, used to check for seasonal outliers |

### Key Findings

- **40,010 production orders** in plant 1000, calendar year 2025; **39,094 productive orders** (ZP01 + ZP02).
- **161 orders per working day** on average, based on total order volume (40,010 orders ÷ 248 working days, plant Augsburg, 2025).
- Near-equal **MTS/ETO split**: 55.1% ZP01 (Lagerfertigung) vs. 42.6% ZP02 (Kundeneinzelfertigung) — confirms a genuinely hybrid production environment.
- **Controller 212** (actuator line, AG9 pilot resource) is the **second-highest volume controller in the entire plant**, with 4,257 productive orders (10.6% of total plant volume).
- The four-controller pilot scope (211, 212, 415, 416) accounts for **13.8%** of total productive order volume.
- No seasonal outliers in monthly distribution (range: 1,775–3,908 orders/month; December dip explained by year-end shutdown).

---

## Setup

```bash
# Install dependencies
pip install pandas openpyxl

# Configure file paths and column names in the CONFIGURATION section
# of the script you want to run, then execute from the repository root:
python src/analyse_md06.py
python src/analyse_coois.py
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

- [ ] Power BI dashboard combining `md06_summary.csv` and `coois_summary.csv`
- [ ] Post-implementation comparison (after PP/DS go-live)
- [x] Working-day baseline corrected to 248 days (was 252) — confirmed and propagated across thesis chapters
