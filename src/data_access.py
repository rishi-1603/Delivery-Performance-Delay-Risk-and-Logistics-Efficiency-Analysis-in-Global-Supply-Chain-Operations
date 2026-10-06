"""Single data-access entry point used by the dashboard.

Resolution order:
1. ``data/processed/apl_clean.csv`` — the local development path, built by
   ``scripts/01_clean_data.py`` from the raw CSV.
2. GitHub Release asset — the deployment path. The 62.5 MB raw CSV is too
   large for git, so a fresh checkout (e.g. Streamlit Cloud) has no data
   directory. On first load the app downloads the pinned ``data-v1`` asset
   and cleans it in memory; ``st.cache_data`` keeps it for the lifetime of
   the container, so only the first request pays the download cost.
"""
from __future__ import annotations

import io
import urllib.request

import pandas as pd

from . import config as C

# Pinned dataset release (public repo — no auth required). If this repo is
# forked, create your own `data-v1` release or point this at the upstream.
RAW_RELEASE_URL = (
    "https://github.com/rishi-1603/"
    "Delivery-Performance-Delay-Risk-and-Logistics-Efficiency-Analysis-in-Global-Supply-Chain-Operations"
    "/releases/download/data-v1/APL_Logistics.csv"
)


def get_processed_df() -> pd.DataFrame:
    """Return the cleaned dataset — from disk when present, else from the release."""
    if C.PROCESSED_CSV.exists():
        return pd.read_csv(C.PROCESSED_CSV, low_memory=False)

    from .data_cleaning import clean  # deferred: only needed on the cloud path

    request = urllib.request.Request(
        RAW_RELEASE_URL, headers={"User-Agent": "apl-logistics-dashboard"}
    )
    with urllib.request.urlopen(request) as response:
        raw_bytes = response.read()
    raw = pd.read_csv(io.BytesIO(raw_bytes), low_memory=False, encoding=C.RAW_ENCODING)
    df, _ = clean(raw)
    return df
