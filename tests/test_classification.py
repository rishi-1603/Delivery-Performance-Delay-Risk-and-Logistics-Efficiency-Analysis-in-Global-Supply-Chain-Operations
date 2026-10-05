"""Classification tests — the official Early/On-time/Delayed methodology."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import classify_gap  # noqa: E402


def test_classify_gap_rules():
    assert classify_gap(-2) == "Early"
    assert classify_gap(-1) == "Early"
    assert classify_gap(0) == "On-time"
    assert classify_gap(1) == "Delayed"
    assert classify_gap(4) == "Delayed"


def test_classification_pinned_counts(df):
    counts = df["delivery_class"].value_counts()
    assert int(counts["Early"]) == 43_366
    assert int(counts["On-time"]) == 33_753
    assert int(counts["Delayed"]) == 103_400
    assert len(df) == 180_519


def test_gap_is_real_minus_scheduled(df):
    calc = df["Days for shipping (real)"] - df["Days for shipment (scheduled)"]
    assert (calc == df["delivery_delay_gap"]).all()


def test_gap_range(df):
    # verified dataset property: gaps span -2..+4 days
    assert df["delivery_delay_gap"].min() == -2
    assert df["delivery_delay_gap"].max() == 4
