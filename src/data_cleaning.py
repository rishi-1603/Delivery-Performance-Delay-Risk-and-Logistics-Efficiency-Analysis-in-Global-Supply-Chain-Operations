"""Data cleaning pipeline: raw APL Logistics CSV -> validated analytical dataset.

Design rules (docs/methodology.md):
- The RAW file is never modified. This pipeline writes data/processed/apl_clean.csv.
- No rows are deleted. Canceled shipments are FLAGGED (is_canceled), not removed,
  so every KPI can be reported on both the all-shipments basis (official) and the
  delivered-shipments basis (sensitivity view).
- Every transformation is logged and reproducible.
"""
from __future__ import annotations

import pandas as pd
import numpy as np

from . import config as C


def load_raw(path=None) -> pd.DataFrame:
    """Load the raw CSV with its true encoding (latin-1)."""
    path = path or C.RAW_CSV
    return pd.read_csv(path, low_memory=False, encoding=C.RAW_ENCODING)


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Clean + enrich. Returns (cleaned_df, transformation_log)."""
    log: list[dict] = []

    def record(step: str, detail: str):
        log.append({"step": step, "detail": detail})

    out = df.copy()
    record("load", f"{len(out):,} rows x {len(out.columns)} columns read (latin-1)")

    # 1. Whitespace strip on text columns (idempotent, non-destructive)
    obj_cols = out.select_dtypes(include="object").columns
    stripped = {c: (out[c] != out[c].str.strip()).sum() for c in obj_cols}
    n_strip = int(sum(stripped.values()))
    for c in obj_cols:
        out[c] = out[c].str.strip()
    record("whitespace", f"stripped leading/trailing whitespace in {n_strip} cell(s) across text columns")

    # 2. Duplicate check (no deletion without cause)
    n_dupes = int(out.duplicated().sum())
    record("duplicates", f"{n_dupes} exact duplicate rows found (expected 0; nothing deleted)")

    # 3. Standardize Customer Country ('EE. UU.' is Spanish for USA)
    n_fix = int((out[C.COL_CUSTOMER_COUNTRY] == "EE. UU.").sum())
    out[C.COL_CUSTOMER_COUNTRY] = out[C.COL_CUSTOMER_COUNTRY].replace(C.COUNTRY_FIXES)
    record(
        "standardize_country",
        f"Customer Country: {n_fix:,} rows 'EE. UU.' -> 'United States' "
        "(Spanish spelling; Order Country accents preserved as-is)",
    )

    # 4. Numeric validation: shipping day fields must be non-negative integers
    for col in (C.COL_DAYS_REAL, C.COL_DAYS_SCHED):
        bad = int((out[col] < 0).sum())
        assert bad == 0, f"invalid negative durations in {col}: {bad}"
        assert str(out[col].dtype).startswith("int"), f"{col} not integer-typed"
    record("numeric_validation", "Days for shipping (real) / (scheduled): all non-negative integers — pass")

    # 5. Risk flag domain check
    bad_risk = int((~out[C.COL_RISK].isin([0, 1])).sum())
    assert bad_risk == 0, f"Late_delivery_risk has values outside {{0,1}}: {bad_risk}"
    record("risk_domain", "Late_delivery_risk in {0,1} for all rows — pass")

    # 6. Derived: delivery delay gap (official definition: real - scheduled)
    out[C.COL_GAP] = out[C.COL_DAYS_REAL] - out[C.COL_DAYS_SCHED]
    record(
        "delivery_gap",
        "delivery_delay_gap = Days for shipping (real) - Days for shipment (scheduled)",
    )

    # 7. Derived: official classification
    out[C.COL_CLASS] = out[C.COL_GAP].apply(C.classify_gap)
    record(
        "classification",
        "delivery_class: Early (gap<0) / On-time (gap==0) / Delayed (gap>0)",
    )

    # 8. Derived: canceled flag (never deleted — KPIs reported on both bases)
    out[C.COL_CANCELED] = out[C.COL_DELIVERY_STATUS] == C.CANCELED_STATUS
    n_canceled = int(out[C.COL_CANCELED].sum())
    record(
        "cancel_flag",
        f"{n_canceled:,} rows flagged is_canceled (Delivery Status == 'Shipping canceled') — "
        "kept in data; excluded only in the documented delivered-basis sensitivity view",
    )

    # 9. Missing values: documented, not imputed
    missing = out.isna().sum()
    missing = missing[missing > 0]
    record(
        "missing_values",
        "left as-is (not imputed): "
        + ", ".join(f"{c} ({v})" for c, v in missing.items())
        + " — none affect delivery KPIs",
    )

    return out, log


def build_processed(write: bool = True) -> tuple[pd.DataFrame, list[dict]]:
    """End-to-end: load raw -> clean -> (optionally) write processed CSV."""
    df, log = clean(load_raw())
    if write:
        C.PROCESSED_CSV.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(C.PROCESSED_CSV, index=False, encoding="utf-8")
        log.append({"step": "write", "detail": f"processed dataset written to {C.PROCESSED_CSV.name} (utf-8)"})
    return df, log
