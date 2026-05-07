"""
analyse_md06.py
===============
MD06 Exception Message Analysis — Erhardt+Leimer GmbH
Supply-Chain-Analytics Portfolio Project

Analyzes SAP MD06 exports for four MRP controllers (Disponenten 211, 212, 415, 416).
Each file may contain multiple demand lines per material — analysis is performed at
material level (deduplicated), assigning the worst-case status per material.

Status code legend (three-character SAP MD06 ampel system):
  Position 1: Exception group alarm   (X = red, O = no alarm)
  Position 2: Stock coverage alarm    (X = red, O = no alarm)
  Position 3: Processed/confirmed     (X = yes, O = no)

  XOO = Unprocessed exception message -> action required
  OXO = Stock coverage warning        -> range alarm, no exception
  OOX = Processed/confirmed           -> no immediate action required

Outputs:
  - output/md06_report.md     Human-readable Markdown report
  - output/md06_summary.csv   Machine-readable KPI table (Power BI input)

Usage:
  python src/analyse_md06.py

Dependencies:
  pip install pandas openpyxl
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# ---------------------------------------------
# CONFIGURATION
# ---------------------------------------------

FILES = {
    "211": Path("data/MD06_Ausnahmemeldungen_211.xlsx"),
    "212": Path("data/MD06_Ausnahmemeldungen_212.xlsx"),
    "415": Path("data/MD06_Ausnahmemeldungen_415.xlsx"),
    "416": Path("data/MD06_Ausnahmemeldungen_416.xlsx"),
}

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

COL_STATUS   = "Status"
COL_MATERIAL = "Material"
COL_GROUP    = [f"Ausnahmengruppe {i}" for i in range(1, 9)]
COL_COVERAGE = "Bestandsreichweite"
COL_ABC      = "ABC-Kennzeichen"
COL_MATTYPE  = "Materialart"

STATUS_PRIORITY = {"XOO": 0, "OXO": 1, "OOX": 2}

# ---------------------------------------------
# LOAD & DEDUPLICATE TO MATERIAL LEVEL
# ---------------------------------------------

def load_file(dispo: str, path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"File not found for Disponent {dispo}: {path}\n"
            "Place your MD06 exports in the data/ folder."
        )
    df = pd.read_excel(path, dtype=str)
    df.columns = df.columns.str.strip()
    df = df.fillna("")
    raw_rows = len(df)

    df["_prio"] = df[COL_STATUS].map(STATUS_PRIORITY).fillna(99)
    df_mat = (
        df.sort_values("_prio")
          .drop_duplicates(subset=[COL_MATERIAL], keep="first")
          .drop(columns=["_prio"])
          .copy()
    )
    print(f"  [OK] Disponent {dispo}: {raw_rows:,} rows -> {len(df_mat):,} unique materials")
    return df_mat


def load_all() -> dict:
    print("\n-- Loading & deduplicating MD06 exports --")
    return {dispo: load_file(dispo, path) for dispo, path in FILES.items()}

# ---------------------------------------------
# ANALYSIS
# ---------------------------------------------

def safe_float(series: pd.Series) -> pd.Series:
    return (
        series.str.replace(".", "", regex=False)
               .str.replace(",", ".", regex=False)
               .replace("", "0")
               .astype(float)
    )


def analyse_dispo(dispo: str, df: pd.DataFrame) -> dict:
    total = len(df)
    if total == 0:
        return {"dispo": dispo, "total": 0}

    xoo = int((df[COL_STATUS] == "XOO").sum())
    oxo = int((df[COL_STATUS] == "OXO").sum())
    oox = int((df[COL_STATUS] == "OOX").sum())

    xoo_df = df[df[COL_STATUS] == "XOO"].copy()
    if len(xoo_df) > 0 and COL_COVERAGE in xoo_df.columns:
        cov = safe_float(xoo_df[COL_COVERAGE])
        neg_coverage      = int((cov < 0).sum())
        neg_coverage_rate = round(neg_coverage / len(xoo_df) * 100, 1)
        median_coverage   = round(float(cov.median()), 1)
        min_coverage      = round(float(cov.min()), 1)
    else:
        neg_coverage = neg_coverage_rate = 0
        median_coverage = min_coverage = None

    abc_counts = {}
    if len(xoo_df) > 0 and COL_ABC in xoo_df.columns:
        abc_counts = xoo_df[COL_ABC].value_counts().to_dict()

    group_counts = {}
    for col in COL_GROUP:
        if col in df.columns:
            flagged = int((df[col].str.strip() != "").sum())
            if flagged > 0:
                group_counts[f"Gruppe {col.split()[-1]}"] = flagged

    mattype_counts = {}
    if len(xoo_df) > 0 and COL_MATTYPE in xoo_df.columns:
        mattype_counts = xoo_df[COL_MATTYPE].value_counts().to_dict()

    return {
        "dispo":                dispo,
        "total":                total,
        "xoo":                  xoo,
        "oxo":                  oxo,
        "oox":                  oox,
        "xoo_rate":             round(xoo / total * 100, 1),
        "oxo_rate":             round(oxo / total * 100, 1),
        "oox_rate":             round(oox / total * 100, 1),
        "neg_coverage":         neg_coverage,
        "neg_coverage_rate":    neg_coverage_rate,
        "median_coverage_days": median_coverage if median_coverage is not None else "n/a",
        "min_coverage_days":    min_coverage    if min_coverage    is not None else "n/a",
        "abc_counts":           abc_counts,
        "group_counts":         group_counts,
        "mattype_counts":       mattype_counts,
    }


def analyse_all(data: dict) -> list:
    print("\n-- Analysing exception messages (material level) --")
    results = []
    for dispo, df in data.items():
        r = analyse_dispo(dispo, df)
        results.append(r)
        print(f"  [OK] Disponent {r['dispo']}: "
              f"XOO {r['xoo_rate']}% | OXO {r['oxo_rate']}% | OOX {r['oox_rate']}%")
    return results

# ---------------------------------------------
# OUTPUT -- MARKDOWN REPORT
# ---------------------------------------------

def fmt_abc(abc: dict) -> str:
    return " | ".join(f"{k}: {v}" for k, v in sorted(abc.items())) or "n/a"

def fmt_groups(groups: dict) -> str:
    return " | ".join(f"{k}: {v}" for k, v in sorted(groups.items())) or "keine"


def write_markdown(results: list):
    today = datetime.today().strftime("%d.%m.%Y")
    lines = []

    lines += [
        "# MD06 Ausnahmemeldungsanalyse -- Erhardt+Leimer GmbH",
        f"\n**Auswertungsdatum:** {today}  ",
        "**Scope:** Disponenten 211, 212, 415, 416  ",
        "**Analyseebene:** Materialnummer (dedupliziert -- schlimmster Status je Material)  ",
        "**Quelle:** SAP MD06-Export  ",
        "**Verwendung:** Kapitel 3.3 -- Ist-Analyse Planungsqualitat\n",
        "---\n",
        "## Statuscode-Legende\n",
        "| Code | Bedeutung | Handlungsbedarf |",
        "|---|---|---|",
        "| **XOO** | Ausnahmemeldung vorhanden -- nicht bearbeitet | **Ja** |",
        "| **OXO** | Bestandsreichweiten-Alarm -- keine Ausnahme | Ja (Reichweite) |",
        "| **OOX** | Ausnahmemeldung bearbeitet/bestatigt | Nein |",
        "",
        "> Drei-Zeichen-Ampelsystem: Position 1 = Ausnahmengruppen-Alarm | "
        "Position 2 = Reichweiten-Alarm | Position 3 = Bearbeitet\n",
        "---\n",
        "## 1. Ubersicht -- Ausnahmemeldungsquoten (Materialebene)\n",
        "| Disponent | Materialien | XOO (%) | OXO (%) | OOX (%) |",
        "|---|---|---|---|---|",
    ]

    for r in results:
        lines.append(
            f"| {r['dispo']} | {r['total']:,} | **{r['xoo_rate']}%** "
            f"| {r['oxo_rate']}% | {r['oox_rate']}% |"
        )

    total_all = sum(r["total"] for r in results)
    xoo_all   = sum(r["xoo"]   for r in results)
    oxo_all   = sum(r["oxo"]   for r in results)
    oox_all   = sum(r["oox"]   for r in results)
    xoo_rate_all = round(xoo_all / total_all * 100, 1) if total_all else 0
    oxo_rate_all = round(oxo_all / total_all * 100, 1) if total_all else 0
    oox_rate_all = round(oox_all / total_all * 100, 1) if total_all else 0

    lines += [
        f"| **Gesamt** | **{total_all:,}** | **{xoo_rate_all}%** "
        f"| **{oxo_rate_all}%** | **{oox_rate_all}%** |",
        "\n---\n",
        "## 2. Bestandsreichweite (XOO-Materialien)\n",
        "| Disponent | XOO-Materialien | Median (Tage) | Minimum (Tage) | Negativbestand |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['dispo']} | {r['xoo']:,} | {r['median_coverage_days']} "
            f"| {r['min_coverage_days']} | {r['neg_coverage_rate']}% |"
        )

    lines += ["\n---\n", "## 3. Detailauswertung je Disponent\n"]
    for r in results:
        lines += [
            f"### Disponent {r['dispo']}\n",
            f"- **Materialien gesamt:** {r['total']:,}",
            f"- **XOO (unbearbeitet):** {r['xoo']:,} ({r['xoo_rate']}%)",
            f"- **OXO (Reichweiten-Alarm):** {r['oxo']:,} ({r['oxo_rate']}%)",
            f"- **OOX (bearbeitet):** {r['oox']:,} ({r['oox_rate']}%)",
            f"- **Negativbestand (XOO):** {r['neg_coverage']:,} Materialien "
            f"({r['neg_coverage_rate']}%)",
            f"- **ABC-Verteilung (XOO):** {fmt_abc(r['abc_counts'])}",
            f"- **Ausnahmengruppen:** {fmt_groups(r['group_counts'])}",
            "",
        ]

    dispo212_total = next(r["total"] for r in results if r["dispo"] == "212")
    lines += [
        "---\n",
        "## 4. Kernbefunde fur Kapitel 3.3\n",
        f"- **Gesamtquote unbearbeiteter Ausnahmemeldungen (XOO):** {xoo_rate_all}% "
        f"({xoo_all:,} von {total_all:,} Materialien im Scope)",
        f"- **Zusatzlicher Reichweiten-Alarm (OXO):** {oxo_all:,} Materialien "
        f"({oxo_rate_all}%) -- Bestandsreichweite kritisch, keine formale Ausnahmemeldung",
        "- Die XOO-Quote dient als Baseline-KPI fur die Evaluation in Kapitel 5: "
        "Eine Reduktion nach PP/DS-Einfuhrung ware ein messbarer Wirksamkeitsnachweis.",
        f"- Disponent 212 (Stellantriebe, Pilotarbeitsplatz AG9) ist mit "
        f"{dispo212_total:,} Materialien der volumenstarkste Disponent im Scope.",
        "\n---\n",
        f"*Erstellt: {today} | Autor: Maximilian Karle | Masterarbeit WI -- MCI 2026*",
    ]

    report_path = OUTPUT_DIR / "md06_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  [OK] Markdown report -> {report_path}")


# ---------------------------------------------
# OUTPUT -- CSV (Power BI Input)
# ---------------------------------------------

def write_csv(results: list):
    rows = [{
        "disponent":             r["dispo"],
        "total_materials":       r["total"],
        "xoo_count":             r["xoo"],
        "oxo_count":             r["oxo"],
        "oox_count":             r["oox"],
        "xoo_rate_pct":          r["xoo_rate"],
        "oxo_rate_pct":          r["oxo_rate"],
        "oox_rate_pct":          r["oox_rate"],
        "neg_coverage_count":    r["neg_coverage"],
        "neg_coverage_rate_pct": r["neg_coverage_rate"],
        "median_coverage_days":  r["median_coverage_days"],
        "min_coverage_days":     r["min_coverage_days"],
    } for r in results]

    csv_path = OUTPUT_DIR / "md06_summary.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False, sep=";", decimal=",", encoding="utf-8-sig")
    print(f"  [OK] CSV summary -> {csv_path}")


# ---------------------------------------------
# MAIN
# ---------------------------------------------

def main():
    print("=" * 55)
    print("MD06 Exception Analysis -- Erhardt+Leimer GmbH")
    print("=" * 55)
    data    = load_all()
    results = analyse_all(data)
    write_markdown(results)
    write_csv(results)
    print("\n-- Done --")
    print("  Report : output/md06_report.md")
    print("  CSV    : output/md06_summary.csv")
    print("=" * 55)


if __name__ == "__main__":
    main()
