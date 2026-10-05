"""Shared fixtures — load the processed dataset once per test session.
If the raw data is absent (e.g., minimal CI), data-dependent tests skip."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config as C  # noqa: E402


@pytest.fixture(scope="session")
def df() -> pd.DataFrame:
    if not C.PROCESSED_CSV.exists():
        pytest.skip("processed dataset not present — run scripts/01_clean_data.py with the raw data")
    return pd.read_csv(C.PROCESSED_CSV, low_memory=False)
