"""
analyse_md06.py
===============
MD06 Exception Message Analysis — ELA (anonymised industrial case)
Supply-Chain-Analytics Portfolio Project

Context:
  The case company operates a hybrid MTS/ETO production environment.
  SAP MD06 is not actively used by planners — exception messages accumulate
  without systematic review. The OOX "processed" indicator is set automatically
  by SAP when the same exception persists across MRP runs, NOT by planner action.
  Therefore XOO vs. OOX is NOT a reliable measure of planner activity.

What this script measures (thesis-relevant):
  1. How many materials carry ANY exception message (regardless of status)?
  2. Which exception groups dominate (planning urgency)?
  3. What is the stock coverage situation for materials with exceptions?
  4. ABC classification of exception materials (criticality proxy)?

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

COMPANY_ALIAS = "ELA"  # Anonymised alias — do not change to real company name

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

# Exception group descriptions (SAP standard)
GROUP_LABELS = {
    "1": "Eroeffnungstermin in Vergangenheit",
    "2": "Starttermin in Vergangenheit",
    "3": "Endtermin in Vergangenheit",
    "4": "Allgemeine Meldungen (informativ)",
    "5": "Fehler bei Stuecklistenaufloesung",
    "6": "Verfuegbarkeitspruefung / Bestandsabweichung",
    "7": "Umterminierung erforderlich",
    "8": "Planungsabbruch (kritisch)",
}

# Priority for worst-case status aggregation per material
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

    # Deduplicate to material level — keep worst-case status
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

    # Core thesis metric: ALL materials with any exception message
    # Status XOO/OXO/OOX distinction is NOT reliable at ELA
    # (OOX is set automatically by SAP, not by planner action)
    with_exception = total  # All rows in MD06 export have at least one exception
    without_exception = 0   # Materials without exceptions do not appear in MD06

    # Stock coverage for all exception materials
    if COL_COVERAGE in df.columns:
        cov = safe_float(df[COL_COVERAGE])
        neg_coverage      = int((cov < 0).sum())
        neg_coverage_rate = round(neg_coverage / total * 100, 1)
        median_coverage   = round(float(cov.median()), 1)
        min_coverage      = round(float(cov.min()), 1)
        zero_coverage     = int((cov <= 0).sum())
        zero_coverage_rate = round(zero_coverage / total * 100, 1)
    else:
        neg_coverage = neg_coverage_rate = 0
        zero_coverage = zero_coverage_rate = 0
        median_coverage = min_coverage = None

    # ABC distribution of exception materials
    abc_counts = {}
    if COL_ABC in df.columns:
        abc_counts = df[COL_ABC].value_counts().to_dict()

    # Exception group breakdown — how many materials per group
    group_counts = {}
    for col in COL_GROUP:
        if col in df.columns:
            flagged = int((df[col].str.strip() != "").sum())
            if flagged > 0:
                num = col.split()[-1]
                group_counts[num] = flagged

    # Material type breakdown
    mattype_counts = {}
    if COL_MATTYPE in df.columns:
        mattype_counts = df[COL_MATTYPE].value_counts().to_dict()

    # Status breakdown — for reference only, not primary KPI
    xoo = int((df[COL_STATUS] == "XOO").sum())
    oxo = int((df[COL_STATUS] == "OXO").sum())
    oox = int((df[COL_STATUS] == "OOX").sum())

    return {
        "dispo":                dispo,
        "total":                total,
        "with_exception":       with_exception,
        "xoo":                  xoo,
        "oxo":                  oxo,
        "oox":                  oox,
        "neg_coverage":         neg_coverage,
        "neg_coverage_rate":    neg_coverage_rate,
        "zero_coverage":        zero_coverage,
        "zero_coverage_rate":   zero_coverage_rate,
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
              f"{r['total']:,} materials with exceptions | "
              f"Negative coverage: {r['neg_coverage_rate']}%")
    return results

# ---------------------------------------------
# OUTPUT -- MARKDOWN REPORT
# ---------------------------------------------

def fmt_abc(abc: dict) -> str:
    out = []
    for k in ["A", "B", "C", ""]:
        if k in abc:
            label = k if k else "kein ABC"
            out.append(f"{label}: {abc[k]}")
    return " | ".join(out) or "n/a"

def fmt_groups(groups: dict) -> str:
    if not groups:
        return "keine"
    parts = []
    for num, count in sorted(groups.items(), key=lambda x: int(x[0])):
        label = GROUP_LABELS.get(num, f"Gruppe {num}")
        parts.append(f"Gr.{num} ({label}): {count}")
    return "\n  - ".join(parts)


def write_markdown(results: list):
    today = datetime.today().strftime("%d.%m.%Y")
    lines = []

    lines += [
        f"# MD06 Ausnahmemeldungsanalyse -- {COMPANY_ALIAS}",
        f"\n**Auswertungsdatum:** {today}  ",
        "**Scope:** MRP-Controller 211, 212, 415, 416  ",
        "**Analyseebene:** Materialnummer (dedupliziert)  ",
        "**Quelle:** SAP MD06-Export (nach MRP-Lauf)  ",
        "**Verwendung:** Baseline-Analyse vor SAP PP/DS-Einfuehrung\n",
        "---\n",
        "## Methodische Vorbemerkung\n",
        "SAP MD06 wird im untersuchten Unternehmen nicht aktiv durch Disponenten genutzt.",
        "Der Bearbeitungsstatus (XOO/OOX) ist daher **kein zuverlaessiger Indikator**",
        "fuer Planungsaktivitaet: OOX bedeutet lediglich, dass SAP dieselbe Ausnahme",
        "beim naechsten MRP-Lauf wiedererkannt und automatisch als 'bekannt' markiert hat --",
        "nicht dass ein Disponent aktiv reagiert hat.",
        "",
        "**Thesis-relevante Kernaussage:** Alle Materialien im MD06-Export tragen",
        "mindestens eine unbehandelte Ausnahmemeldung. Die relevante Frage ist nicht",
        "XOO vs. OOX, sondern: Wie viele Materialien haben Ausnahmemeldungen,",
        "welche Gruppen dominieren, und wie kritisch ist die Bestandssituation?\n",
        "---\n",
        "## 1. Uebersicht -- Materialien mit Ausnahmemeldungen\n",
        "| MRP-Controller | Materialien mit Ausnahmen | Negativbestand (%) | Bestand <= 0 Tage (%) |",
        "|---|---|---|---|",
    ]

    for r in results:
        lines.append(
            f"| {r['dispo']} | {r['total']:,} | {r['neg_coverage_rate']}% "
            f"| {r['zero_coverage_rate']}% |"
        )

    total_all = sum(r["total"] for r in results)
    neg_all   = sum(r["neg_coverage"] for r in results)
    zero_all  = sum(r["zero_coverage"] for r in results)
    neg_rate_all  = round(neg_all  / total_all * 100, 1) if total_all else 0
    zero_rate_all = round(zero_all / total_all * 100, 1) if total_all else 0

    lines += [
        f"| **Gesamt** | **{total_all:,}** | **{neg_rate_all}%** | **{zero_rate_all}%** |",
        "",
        "> Hinweis: Alle aufgefuehrten Materialien haben mindestens eine Ausnahmemeldung.",
        "> Materialien ohne jegliche Ausnahme erscheinen nicht im MD06-Export.\n",
        "---\n",
        "## 2. Bestandsreichweite (alle Ausnahmematerialien)\n",
        "| MRP-Controller | Materialien | Median Reichweite (Tage) | Minimum (Tage) | Negativbestand |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['dispo']} | {r['total']:,} | {r['median_coverage_days']} "
            f"| {r['min_coverage_days']} | {r['neg_coverage']:,} ({r['neg_coverage_rate']}%) |"
        )

    lines += ["\n---\n", "## 3. Ausnahmengruppen-Verteilung\n"]
    lines.append(
        "> Gruppenpriorit\u00e4t nach SAP-Standard: Gr.8 (Planungsabbruch) > Gr.5 (StLi-Fehler) > "
        "Gr.1-3 (Terminueberschreitung) > Gr.7 (Umterminierung) > Gr.6 (Bestand) > Gr.4 (informativ)\n"
    )

    for r in results:
        lines.append(f"### MRP-Controller {r['dispo']}\n")
        if r["group_counts"]:
            lines.append("| Gruppe | Beschreibung | Materialien |")
            lines.append("|---|---|---|")
            for num, count in sorted(r["group_counts"].items(), key=lambda x: int(x[0])):
                label = GROUP_LABELS.get(num, f"Gruppe {num}")
                lines.append(f"| {num} | {label} | {count} |")
        else:
            lines.append("Keine Ausnahmengruppen mit Treffern.")
        lines.append("")

    lines += ["---\n", "## 4. ABC-Verteilung der Ausnahmematerialien\n"]
    lines.append("| MRP-Controller | A-Teile | B-Teile | C-Teile | Kein ABC |")
    lines.append("|---|---|---|---|---|")
    for r in results:
        abc = r["abc_counts"]
        lines.append(
            f"| {r['dispo']} | {abc.get('A', 0)} | {abc.get('B', 0)} "
            f"| {abc.get('C', 0)} | {abc.get('', 0)} |"
        )
    lines.append("")

    lines += ["---\n", "## 5. Bearbeitungsstatus -- nur zur Referenz\n"]
    lines.append(
        "> **Achtung:** XOO/OOX ist bei diesem Unternehmen kein Indikator fuer Planungsaktivitaet.\n"
        "> OOX wird von SAP automatisch gesetzt, wenn dieselbe Ausnahme MRP-laufuebergreifend fortbesteht.\n"
    )
    lines.append("| MRP-Controller | XOO (unquittiert) | OXO (Reichweite) | OOX (auto-quittiert) |")
    lines.append("|---|---|---|---|")
    for r in results:
        lines.append(
            f"| {r['dispo']} | {r['xoo']} ({round(r['xoo']/r['total']*100,1)}%) "
            f"| {r['oxo']} ({round(r['oxo']/r['total']*100,1)}%) "
            f"| {r['oox']} ({round(r['oox']/r['total']*100,1)}%) |"
        )

    lines += ["\n---\n", "## 6. Kernbefunde fuer Kapitel 3.3\n"]
    lines += [
        f"- **{total_all:,} Materialien** im Scope der vier MRP-Controller tragen Ausnahmemeldungen.",
        f"- **{neg_rate_all}%** dieser Materialien ({neg_all:,}) haben negativen Bestandsdeckungsgrad -- aktive Unterdeckung.",
        "- Ausnahmengruppe 4 (allgemeine, informative Meldungen) und Gruppe 7 (Umterminierung) dominieren quantitativ.",
        "- Gruppe 8 (Planungsabbruch) und Gruppe 5 (Stuecklistenfehler) sind qualitativ kritischer -- Einzelfaelle pruefen.",
        "- Die fehlende aktive Nutzung von MD06 bestaetigt das Planungsdefizit: Ausnahmemeldungen laufen systematisch ins Leere.",
        "- Diese Ausgangssituation begruendet den Einsatz von SAP PP/DS Alert Management als strukturierte Eskalationslogik.",
        "\n---\n",
        f"*Erstellt: {today} | Anonymisiertes Industrieprojekt ({COMPANY_ALIAS}) | Masterarbeit WI -- MCI 2026*",
    ]

    report_path = OUTPUT_DIR / "md06_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  [OK] Markdown report -> {report_path}")


# ---------------------------------------------
# OUTPUT -- CSV (Power BI Input)
# ---------------------------------------------

def write_csv(results: list):
    rows = [{
        "mrp_controller":        r["dispo"],
        "total_materials":       r["total"],
        "neg_coverage_count":    r["neg_coverage"],
        "neg_coverage_rate_pct": r["neg_coverage_rate"],
        "zero_coverage_count":   r["zero_coverage"],
        "zero_coverage_rate_pct": r["zero_coverage_rate"],
        "median_coverage_days":  r["median_coverage_days"],
        "min_coverage_days":     r["min_coverage_days"],
        "xoo_count_ref_only":    r["xoo"],
        "oox_count_ref_only":    r["oox"],
        "abc_A":                 r["abc_counts"].get("A", 0),
        "abc_B":                 r["abc_counts"].get("B", 0),
        "abc_C":                 r["abc_counts"].get("C", 0),
        "abc_none":              r["abc_counts"].get("", 0),
    } for r in results]

    csv_path = OUTPUT_DIR / "md06_summary.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False, sep=";", decimal=",", encoding="utf-8-sig")
    print(f"  [OK] CSV summary -> {csv_path}")


# ---------------------------------------------
# MAIN
# ---------------------------------------------

def main():
    print("=" * 55)
    print(f"MD06 Exception Analysis -- {COMPANY_ALIAS} (anonymised)")
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
