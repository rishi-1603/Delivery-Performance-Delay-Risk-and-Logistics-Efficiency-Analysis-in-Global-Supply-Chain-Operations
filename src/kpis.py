"""KPI engine — pure, testable functions. Every number is traceable to the dataset.

KPI definitions and their bases are documented in docs/kpi_dictionary.md.
Two reporting bases are used throughout:
- 'all'        : all 180,519 shipment rows (official spec basis)
- 'delivered'  : excludes 'Shipping canceled' rows (documented sensitivity view)
"""
from __future__ import annotations

import pandas as pd

from . import config as C


def _basis(df: pd.DataFrame, basis: str) -> pd.DataFrame:
    if basis == "all":
        return df
    if basis == "delivered":
        return df[~df[C.COL_CANCELED]]
    raise ValueError(f"unknown basis: {basis}")


# ── KPI 1: On-Time Delivery Rate ────────────────────────────────────────────

def on_time_delivery_rate(df: pd.DataFrame, basis: str = "all") -> dict:
    """% of shipments delivered no later than scheduled (On-time + Early).

    'within scheduled time' is defined as: actual <= scheduled.
    The strict variant (actual == scheduled only) is reported alongside.
    """
    d = _basis(df, basis)
    n = len(d)
    counts = d[C.COL_CLASS].value_counts()
    early = int(counts.get("Early", 0))
    ontime = int(counts.get("On-time", 0))
    delayed = int(counts.get("Delayed", 0))
    return {
        "shipments": n,
        "early": early,
        "on_time": ontime,
        "delayed": delayed,
        "early_pct": round(early / n * 100, 2),
        "on_time_pct_strict": round(ontime / n * 100, 2),
        "on_time_pct": round((early + ontime) / n * 100, 2),  # primary: not late
        "delayed_pct": round(delayed / n * 100, 2),
    }


# ── KPI 2: Average Delivery Delay ───────────────────────────────────────────

def average_delivery_delay(df: pd.DataFrame, basis: str = "all") -> dict:
    """Official KPI: mean of (real - scheduled) across ALL shipments in scope.

    Early deliveries are NOT clipped to zero — the official definition is the
    mean gap, and clipping would hide the early-delivery offset. Supporting
    metrics (delay-among-delayed, median, p90) are reported separately.
    """
    d = _basis(df, basis)
    gaps = d[C.COL_GAP]
    delayed_gaps = gaps[gaps > 0]
    return {
        "avg_gap_days": round(gaps.mean(), 3),
        "median_gap_days": float(gaps.median()),
        "p90_gap_days": float(gaps.quantile(0.9)),
        "avg_delay_when_delayed_days": round(delayed_gaps.mean(), 3),
        "avg_real_days_delayed": round(d.loc[delayed_gaps.index, C.COL_DAYS_REAL].mean(), 2),
    }


# ── KPI 3: Late Delivery Risk Ratio ─────────────────────────────────────────

def late_delivery_risk_ratio(df: pd.DataFrame, basis: str = "all") -> dict:
    """Share of shipments with Late_delivery_risk == 1 (the dataset's own flag).

    Deliberately distinct from the calculated delayed-%; the disagreement is
    quantified in analytics.risk_vs_classification().
    """
    d = _basis(df, basis)
    n = len(d)
    risk1 = int(d[C.COL_RISK].sum())
    return {
        "shipments": n,
        "risk_1": risk1,
        "risk_ratio_pct": round(risk1 / n * 100, 2),
        "risk_0": n - risk1,
    }


# ── KPI 4: Shipping Mode Efficiency ─────────────────────────────────────────

def shipping_mode_efficiency(df: pd.DataFrame, basis: str = "all") -> pd.DataFrame:
    """Transparent mode comparison. Efficiency Index = on-time-or-early share
    (= 100% - delayed%). No arbitrary weighting — every component is shown.
    """
    d = _basis(df, basis)
    n = len(d)
    g = d.groupby(C.COL_SHIP_MODE).agg(
        volume=(C.COL_GAP, "count"),
        delayed=(C.COL_CLASS, lambda x: int((x == "Delayed").sum())),
        on_time=(C.COL_CLASS, lambda x: int((x == "On-time").sum())),
        early=(C.COL_CLASS, lambda x: int((x == "Early").sum())),
        avg_gap_days=(C.COL_GAP, "mean"),
        avg_delay_when_delayed_days=(C.COL_GAP, lambda x: x[x > 0].mean()),
        risk_ratio=(C.COL_RISK, "mean"),
        sales_exposure=(C.COL_SALES, "sum"),
    ).reset_index()
    g["volume_pct"] = (g["volume"] / n * 100).round(1)
    g["delayed_pct"] = (g["delayed"] / g["volume"] * 100).round(2)
    g["efficiency_index_pct"] = (100 - g["delayed_pct"]).round(2)
    g["avg_gap_days"] = g["avg_gap_days"].round(3)
    g["avg_delay_when_delayed_days"] = g["avg_delay_when_delayed_days"].round(2)
    g["risk_ratio_pct"] = (g["risk_ratio"] * 100).round(2)
    g["sales_exposure"] = g["sales_exposure"].round(0)
    return g.sort_values("volume", ascending=False).reset_index(drop=True)


# ── KPI 5: Regional Delay Index ─────────────────────────────────────────────

def regional_delay_index(df: pd.DataFrame, min_volume: int = 0, basis: str = "all") -> pd.DataFrame:
    """Delay intensity by region. The index is the delayed share itself — shown
    WITH volume and delayed count so small-sample regions are never misread."""
    d = _basis(df, basis)
    g = d.groupby(C.COL_REGION).agg(
        volume=(C.COL_GAP, "count"),
        delayed=(C.COL_CLASS, lambda x: int((x == "Delayed").sum())),
        avg_gap_days=(C.COL_GAP, "mean"),
        risk_ratio_pct=(C.COL_RISK, lambda x: x.mean() * 100),
        sales_exposure=(C.COL_SALES, "sum"),
    ).reset_index()
    g["delayed_pct"] = (g["delayed"] / g["volume"] * 100).round(2)
    g["avg_gap_days"] = g["avg_gap_days"].round(3)
    g["risk_ratio_pct"] = g["risk_ratio_pct"].round(2)
    g["sales_exposure"] = g["sales_exposure"].round(0)
    g = g.sort_values("delayed_pct", ascending=False).reset_index(drop=True)
    if min_volume:
        g = g[g["volume"] >= min_volume].reset_index(drop=True)
    return g
