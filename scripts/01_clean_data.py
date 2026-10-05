"""01_clean_data.py — raw -> processed + data-quality report.

Run:  python scripts/01_clean_data.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_cleaning import build_processed  # noqa: E402
from src import config as C  # noqa: E402


def main() -> None:
    df, log = build_processed(write=True)
    C.REPORTS_DIR.mkdir(exist_ok=True)
    lines = [
        "# Data Quality Report",
        "",
        f"Source: `data/raw/{C.RAW_CSV.name}` (encoding: latin-1) | "
        f"Processed: `data/processed/{C.PROCESSED_CSV.name}` (utf-8)",
        "",
        "## Transformation log",
        "",
        "| Step | Detail |",
        "|---|---|",
    ]
    for entry in log:
        lines.append(f"| {entry['step']} | {entry['detail']} |")

    lines += [
        "",
        "## Dataset profile",
        "",
        f"- Rows: {len(df):,} (order-item grain — see methodology)",
        f"- Columns: {len(df.columns)} (40 raw + {len(df.columns) - 40} derived)",
        f"- Exact duplicate rows: {df.duplicated().sum():,}",
        f"- Unique customers: {df['Customer Id'].nunique():,}",
        f"- Order Regions: {df[C.COL_REGION].nunique()} | Markets: {df[C.COL_MARKET].nunique()} "
        f"| Order Countries: {df[C.COL_ORDER_COUNTRY].nunique()}",
        f"- Shipping Modes: {df[C.COL_SHIP_MODE].nunique()} | Categories: {df['Category Name'].nunique()}",
        "",
        "## Known limitations (documented, not 'fixed')",
        "",
        "1. **No date column** — a date-range filter is NOT supported by this dataset.",
        "2. **No Order Id** — the grain is order-ITEM; order-level KPIs are impossible.",
        "   All rates are per-shipment-row and documented as such.",
        "3. **Canceled shipments (7,754 rows)** carry gap values; they are flagged,",
        "   never deleted. Official KPIs use the all-rows basis; a delivered-only",
        "   sensitivity view is provided alongside.",
        "4. **'EE. UU.'** in Customer Country (Spanish for USA) standardized to",
        "   'United States'; accented Order Country names preserved.",
        "5. Missing values (8 Customer Lname, 3 Customer Zipcode) left as-is —",
        "   neither affects delivery KPIs.",
    ]
    (C.REPORTS_DIR / "data_quality_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"processed: {len(df):,} rows -> {C.PROCESSED_CSV}")
    print(f"report: {C.REPORTS_DIR / 'data_quality_report.md'}")


if __name__ == "__main__":
    main()
