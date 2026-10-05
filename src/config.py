"""Configuration: paths, constants, and official methodology rules."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = REPO_ROOT / "data" / "raw" / "APL_Logistics.csv"
PROCESSED_CSV = REPO_ROOT / "data" / "processed" / "apl_clean.csv"
REPORTS_DIR = REPO_ROOT / "reports"

# Source encoding: the raw file uses latin-1 (accented city/country names).
RAW_ENCODING = "latin-1"

# Official column names (kept exactly as shipped — no silent renames)
COL_TYPE = "Type"
COL_DAYS_REAL = "Days for shipping (real)"
COL_DAYS_SCHED = "Days for shipment (scheduled)"
COL_DELIVERY_STATUS = "Delivery Status"
COL_RISK = "Late_delivery_risk"
COL_MARKET = "Market"
COL_REGION = "Order Region"
COL_ORDER_COUNTRY = "Order Country"
COL_ORDER_STATE = "Order State"
COL_CUSTOMER_COUNTRY = "Customer Country"
COL_SEGMENT = "Customer Segment"
COL_SHIP_MODE = "Shipping Mode"
COL_SALES = "Sales"
COL_ORDER_ITEM_TOTAL = "Order Item Total"
COL_PROFIT_PER_ORDER = "Order Profit Per Order"
COL_BENEFIT = "Benefit per order"

# Derived columns (prefixed to avoid clashing with raw names)
COL_GAP = "delivery_delay_gap"
COL_CLASS = "delivery_class"          # Early / On-time / Delayed
COL_CANCELED = "is_canceled"          # Delivery Status == 'Shipping canceled'

CANCELED_STATUS = "Shipping canceled"
LATE_STATUS = "Late delivery"

# Documented standardizations (see docs/data_quality_report.md)
COUNTRY_FIXES = {"EE. UU.": "United States"}  # Spanish spelling of USA in Customer Country


def classify_gap(gap):
    """Official classification (Phase 4 of the spec).

    actual < scheduled -> Early | equal -> On-time | greater -> Delayed
    """
    if gap < 0:
        return "Early"
    if gap == 0:
        return "On-time"
    return "Delayed"
