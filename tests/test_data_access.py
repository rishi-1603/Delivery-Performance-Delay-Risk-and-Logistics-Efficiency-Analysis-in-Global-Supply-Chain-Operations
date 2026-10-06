"""Data-access tests — the single entry point the dashboard relies on."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config as C  # noqa: E402
from src.data_access import RAW_RELEASE_URL, get_processed_df  # noqa: E402


def test_release_url_is_pinned_to_the_data_v1_asset():
    # The cloud fallback must fetch the pinned dataset release, never a moving target.
    assert RAW_RELEASE_URL.startswith("https://github.com/rishi-1603/")
    assert RAW_RELEASE_URL.endswith("/releases/download/data-v1/APL_Logistics.csv")


def test_get_processed_df_returns_the_pinned_dataset():
    if not C.PROCESSED_CSV.exists():
        pytest.skip("processed dataset not present — run scripts/01_clean_data.py first")
    d = get_processed_df()
    assert len(d) == 180_519
    counts = d["delivery_class"].value_counts()
    assert int(counts["Early"]) == 43_366
    assert int(counts["On-time"]) == 33_753
    assert int(counts["Delayed"]) == 103_400
