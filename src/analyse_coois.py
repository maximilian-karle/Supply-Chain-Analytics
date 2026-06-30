"""
analyse_coois.py
=================
COOIS Production Order Volume Analysis — ELA
Supply-Chain-Analytics Portfolio Project

Analyzes a SAP COOIS export of production orders for plant 1000, calendar
year 2025. Computes total order volume, MTS/ETO order type split, MRP
controller ranking, the four-controller pilot scope, and monthly
distribution.

Outputs:
  - output/coois_report.md     Human-readable Markdown report
  - output/coois_summary.csv   Machine-readable KPI table (Power BI input)

Usage:
  python src/analyse_coois.py

Dependencies:
  pip install pandas openpyxl
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

INPUT_FILE = Path("data/FA_2025.xlsx")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Column names as exported by SAP COOIS (German labels), confirmed against
# the actual E+L export layout (columns: Auftrag, Material, Auftragsikone,
# Auftragsart, Disponent, Fertigungssteuerer, Werk, Auftragsmenge,
# Mengeneinheit, Starttermin Eck, Endtermin Eck, Meldungstyp Icon,
# Systemstatus, Fertigungsversion, Materialkurztext).
COL_ORDER       = "Auftrag"            # Production order number
COL_ORDER_TYPE  = "Auftragsart"        # ZP01 / ZP02 / ZP03 / ZP04
COL_PLANT       = "Werk"               # Plant, expected "1000"
COL_MRP_CTRL    = "Disponent"          # MRP controller, e.g. "212"
COL_CREATED     = "Starttermin Eck"    # Order start date (eckterminiert), format TT.MM.JJJJ

# Order type classification (E+L-specific, confirmed via interview B.1/B.2)
ORDER_TYPE_LABELS = {
    "ZP01": "Lagerfertigung (MTS)",
    "ZP02": "Kundeneinzelfertigung (ETO)",
    "ZP03": "Nacharbeit / Sonstige",
    "ZP04": "Montageauftrag",
}

# Productive order types = basis for the "FA/Tag" KPI (ZP01 + ZP02 only)
PRODUCTIVE_TYPES = ["ZP01", "ZP02"]

# Pilot scope: the four MRP controllers taken over for the PP/DS rollout
SCOPE_CONTROLLERS = ["211", "212", "415", "416"]

# Working days basis for plant Augsburg, calendar year 2025.
# CORRECTED: 248 working days (252 in the original Auswertung_FA_2025.md was
# an error — pending review across the full thesis document; see PROJEKTSTATUS).
ARBEITSTAGE_2025 = 248

MONTH_ORDER = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]

# ─────────────────────────────────────────────
# LOAD & VALIDATE
# ─────────────────────────────────────────────

def load_file(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}\n"
            f"Place your COOIS export in the data/ folder as FA_2025.xlsx."
        )
    df = pd.read_excel(path)

    required_cols = [COL_ORDER, COL_ORDER_TYPE, COL_PLANT, COL_MRP_CTRL]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise KeyError(
            f"Expected column(s) not found in export: {missing}\n"
            f"Available columns: {list(df.columns)}\n"
            f"Adjust the COL_* constants at the top of this script to match "
            f"your actual COOIS export layout."
        )
    return df


def filter_plant_year(df: pd.DataFrame, plant: str = "1000", year: int = 2025) -> pd.DataFrame:
    df = df.copy()
    df[COL_PLANT] = df[COL_PLANT].astype(str).str.strip()
    df = df[df[COL_PLANT] == plant]

    if COL_CREATED in df.columns:
        df[COL_CREATED] = pd.to_datetime(df[COL_CREATED], format="%d.%m.%Y", errors="coerce")
        df = df[df[COL_CREATED].dt.year == year]

    return df


# ─────────────────────────────────────────────
# ANALYSIS
# ─────────────────────────────────────────────

def total_volume(df: pd.DataFrame) -> dict:
    total = len(df)
    productive = df[df[COL_ORDER_TYPE].isin(PRODUCTIVE_TYPES)]
    productive_count = len(productive)
    rework_count = total - productive_count

    return {
        "fa_gesamt": total,
        "fa_produktiv": productive_count,
        "fa_nacharbeit_sonstige": rework_count,
        "arbeitstage": ARBEITSTAGE_2025,
        # NOTE: bezogen auf Gesamt-FA (nicht nur produktive ZP01+ZP02), gemäß
        # validierter Projektinvariante (161 FA/Tag = 40.010 / 248 Arbeitstage).
        "fa_pro_arbeitstag": round(total / ARBEITSTAGE_2025, 1),
    }


def order_type_split(df: pd.DataFrame) -> pd.DataFrame:
    counts = df[COL_ORDER_TYPE].value_counts()
    total = counts.sum()

    rows = []
    for code, count in counts.items():
        rows.append({
            "Auftragsart": code,
            "Bezeichnung": ORDER_TYPE_LABELS.get(code, "Unbekannt"),
            "Anzahl_FA": int(count),
            "Anteil_Prozent": round(100 * count / total, 1),
        })

    result = pd.DataFrame(rows).sort_values("Anzahl_FA", ascending=False)
    return result


def controller_ranking(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    productive = df[df[COL_ORDER_TYPE].isin(PRODUCTIVE_TYPES)]
    ranking = (
        productive.groupby(COL_MRP_CTRL)
        .size()
        .reset_index(name="FA_ZP01_ZP02")
        .sort_values("FA_ZP01_ZP02", ascending=False)
        .reset_index(drop=True)
    )
    ranking.insert(0, "Rang", ranking.index + 1)
    return ranking.head(top_n)


def scope_analysis(df: pd.DataFrame) -> pd.DataFrame:
    total_productive = len(df[df[COL_ORDER_TYPE].isin(PRODUCTIVE_TYPES)])

    rows = []
    for ctrl in SCOPE_CONTROLLERS:
        sub = df[df[COL_MRP_CTRL].astype(str) == ctrl]
        fa_gesamt = len(sub)
        fa_productive = len(sub[sub[COL_ORDER_TYPE].isin(PRODUCTIVE_TYPES)])
        anteil = round(100 * fa_productive / total_productive, 1) if total_productive else 0.0

        rows.append({
            "Disponent": ctrl,
            "FA_gesamt": fa_gesamt,
            "FA_ZP01_ZP02": fa_productive,
            "Anteil_am_Gesamtwerk_Prozent": anteil,
        })

    result = pd.DataFrame(rows)
    scope_total = pd.DataFrame([{
        "Disponent": "Gesamt Scope",
        "FA_gesamt": result["FA_gesamt"].sum(),
        "FA_ZP01_ZP02": result["FA_ZP01_ZP02"].sum(),
        "Anteil_am_Gesamtwerk_Prozent": round(100 * result["FA_ZP01_ZP02"].sum() / total_productive, 1) if total_productive else 0.0,
    }])
    return pd.concat([result, scope_total], ignore_index=True)


def monthly_distribution(df: pd.DataFrame) -> pd.DataFrame:
    if COL_CREATED not in df.columns:
        return pd.DataFrame(columns=["Monat", "FA"])

    productive = df[df[COL_ORDER_TYPE].isin(PRODUCTIVE_TYPES)].copy()
    productive[COL_CREATED] = pd.to_datetime(productive[COL_CREATED], format="%d.%m.%Y", errors="coerce")
    productive["Monat_Num"] = productive[COL_CREATED].dt.month

    counts = productive.groupby("Monat_Num").size()
    rows = []
    for month_num in range(1, 13):
        month_name = MONTH_ORDER[month_num - 1]
        rows.append({
            "Monat": f"{month_name} 2025",
            "FA": int(counts.get(month_num, 0)),
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# REPORTING
# ─────────────────────────────────────────────

def build_markdown_report(volume: dict, split: pd.DataFrame, ranking: pd.DataFrame,
                           scope: pd.DataFrame, monthly: pd.DataFrame) -> str:
    lines = []
    lines.append("# Auswertung Fertigungsaufträge 2025 — ELA, Werk 1000")
    lines.append("")
    lines.append(f"**Quelle:** SAP COOIS-Export FA_2025.xlsx")
    lines.append(f"**Auswertungsdatum:** {datetime.now().strftime('%d.%m.%Y')}")
    lines.append(f"**Scope:** Werk 1000, Kalenderjahr 2025")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 1. Gesamtvolumen")
    lines.append("")
    lines.append("| Kennzahl | Wert |")
    lines.append("|---|---|")
    lines.append(f"| Fertigungsaufträge gesamt (2025) | {volume['fa_gesamt']:,} |".replace(",", "."))
    lines.append(f"| Davon produktive FA (ZP01 + ZP02) | {volume['fa_produktiv']:,} |".replace(",", "."))
    lines.append(f"| Davon Nacharbeit / Sonstiges | {volume['fa_nacharbeit_sonstige']:,} |".replace(",", "."))
    lines.append(f"| Arbeitstage 2025 | {volume['arbeitstage']} |")
    lines.append(f"| Ø FA pro Arbeitstag (Gesamt-FA, validierte Kennzahl) | **{volume['fa_pro_arbeitstag']}** |")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 2. Auftragsarten — MTS vs. ETO")
    lines.append("")
    lines.append("| Auftragsart | Bezeichnung | Anzahl FA | Anteil |")
    lines.append("|---|---|---|---|")
    for _, row in split.iterrows():
        lines.append(
            f"| {row['Auftragsart']} | {row['Bezeichnung']} | "
            f"{row['Anzahl_FA']:,} | {row['Anteil_Prozent']} % |".replace(",", ".")
        )
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 3. Disponenten-Verteilung (Top 15, ZP01 + ZP02)")
    lines.append("")
    lines.append("| Rang | Disponent | FA (ZP01+ZP02) |")
    lines.append("|---|---|---|")
    for _, row in ranking.iterrows():
        lines.append(f"| {row['Rang']} | {row[COL_MRP_CTRL]} | {row['FA_ZP01_ZP02']:,} |".replace(",", "."))
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append(f"## 4. Pilot-Scope ({', '.join(SCOPE_CONTROLLERS)})")
    lines.append("")
    lines.append("| Disponent | FA gesamt | FA (ZP01+ZP02) | Anteil am Gesamtwerk |")
    lines.append("|---|---|---|---|")
    for _, row in scope.iterrows():
        lines.append(
            f"| {row['Disponent']} | {row['FA_gesamt']:,} | {row['FA_ZP01_ZP02']:,} | "
            f"{row['Anteil_am_Gesamtwerk_Prozent']} % |".replace(",", ".")
        )
    lines.append("")
    lines.append("---")
    lines.append("")

    if not monthly.empty:
        lines.append("## 5. Monatliche Verteilung (ZP01 + ZP02)")
        lines.append("")
        lines.append("| Monat | FA |")
        lines.append("|---|---|")
        for _, row in monthly.iterrows():
            lines.append(f"| {row['Monat']} | {row['FA']:,} |".replace(",", "."))
        lines.append("")

    return "\n".join(lines)


def build_summary_csv(volume: dict, split: pd.DataFrame, scope: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {"Kennzahl": "FA_gesamt_2025", "Wert": volume["fa_gesamt"]},
        {"Kennzahl": "FA_produktiv_2025", "Wert": volume["fa_produktiv"]},
        {"Kennzahl": "FA_pro_Arbeitstag", "Wert": volume["fa_pro_arbeitstag"]},
    ]
    for _, row in split.iterrows():
        rows.append({"Kennzahl": f"FA_{row['Auftragsart']}", "Wert": row["Anzahl_FA"]})
    for _, row in scope.iterrows():
        rows.append({"Kennzahl": f"FA_Scope_{row['Disponent']}", "Wert": row["FA_ZP01_ZP02"]})
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("Loading COOIS export...")
    df_raw = load_file(INPUT_FILE)
    print(f"  {len(df_raw)} rows loaded.")

    df = filter_plant_year(df_raw, plant="1000", year=2025)
    print(f"  {len(df)} rows after filtering for plant 1000 / year 2025.")

    volume = total_volume(df)
    split = order_type_split(df)
    ranking = controller_ranking(df)
    scope = scope_analysis(df)
    monthly = monthly_distribution(df)

    report = build_markdown_report(volume, split, ranking, scope, monthly)
    report_path = OUTPUT_DIR / "coois_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Report written to {report_path}")

    summary = build_summary_csv(volume, split, scope)
    summary_path = OUTPUT_DIR / "coois_summary.csv"
    summary.to_csv(summary_path, index=False, encoding="utf-8")
    print(f"Summary CSV written to {summary_path}")

    print("\nKey figures:")
    print(f"  FA gesamt:           {volume['fa_gesamt']}")
    print(f"  FA produktiv:        {volume['fa_produktiv']}")
    print(f"  FA / Arbeitstag:     {volume['fa_pro_arbeitstag']}")


if __name__ == "__main__":
    main()
