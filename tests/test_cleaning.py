"""Cleaning pipeline tests — reproducibility and data-quality rules."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config as C  # noqa: E402
from src.data_cleaning import load_raw, clean  # noqa: E402


def test_raw_loads_with_expected_shape():
    raw = load_raw()
    assert raw.shape == (180_519, 40)


def test_no_exact_duplicates(df):
    assert df.duplicated().sum() == 0


def test_no_missing_in_kpi_columns(df):
    for col in (
        "Days for shipping (real)",
        "Days for shipment (scheduled)",
        "Delivery Status",
        "Late_delivery_risk",
        "Shipping Mode",
        "Order Region",
        "Market",
        "Customer Segment",
    ):
        assert df[col].notna().all(), col


def test_customer_country_standardized(df):
    # 'EE. UU.' (Spanish for USA) must not survive cleaning
    assert (df[C.COL_CUSTOMER_COUNTRY] == "EE. UU.").sum() == 0
    n_us = (df[C.COL_CUSTOMER_COUNTRY] == "United States").sum()
    assert n_us > 100_000  # the US is the dominant customer country


def test_canceled_flagged_not_deleted(df):
    n_canceled = int(df[C.COL_CANCELED].sum())
    assert n_canceled == 7_754
    assert len(df) == 180_519  # nothing deleted


def test_cleaning_log_documents_every_step():
    raw = load_raw()
    _, log = clean(raw)
    steps = [e["step"] for e in log]
    for expected in ("load", "whitespace", "duplicates", "standardize_country",
                     "numeric_validation", "risk_domain", "delivery_gap",
                     "classification", "cancel_flag", "missing_values"):
        assert expected in steps, expected
