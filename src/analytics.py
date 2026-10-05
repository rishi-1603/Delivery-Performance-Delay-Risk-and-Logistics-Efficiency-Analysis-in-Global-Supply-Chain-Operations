"""Diagnostic analytics: risk-vs-classification, markets, segments, exposure."""
from __future__ import annotations

import pandas as pd

from . import config as C


def risk_vs_classification(df: pd.DataFrame) -> dict:
    """Compare the dataset's Late_delivery_risk flag with the calculated
    gap-based classification. The disagreement pattern is a key finding."""
    delayed = df[C.COL_CLASS] == "Delayed"
    risk1 = df[C.COL_RISK] == 1
    n = len(df)
    both = int((delayed & risk1).sum())
    delayed_only = int((delayed & ~risk1).sum())
    status_of_delayed_only = (
        df.loc[delayed & ~risk1, C.COL_DELIVERY_STATUS].value_counts().to_dict()
    )
    risk1_equals_late_status = int(risk1.sum()) == int((df[C.COL_DELIVERY_STATUS] == C.LATE_STATUS).sum())
    return {
        "shipments": n,
        "gap_delayed": int(delayed.sum()),
        "gap_delayed_pct": round(delayed.sum() / n * 100, 2),
        "risk_1": int(risk1.sum()),
        "risk_1_pct": round(risk1.sum() / n * 100, 2),
        "both_delayed_and_risk1": both,
        "delayed_but_risk0": delayed_only,
        "delayed_but_risk0_status_breakdown": status_of_delayed_only,
        "risk1_equals_late_delivery_status": risk1_equals_late_status,
    }


def market_analysis(df: pd.DataFrame, basis: str = "all") -> pd.DataFrame:
    d = df[~df[C.COL_CANCELED]] if basis == "delivered" else df
    g = d.groupby(C.COL_MARKET).agg(
        volume=(C.COL_GAP, "count"),
        delayed=(C.COL_CLASS, lambda x: int((x == "Delayed").sum())),
        avg_gap_days=(C.COL_GAP, "mean"),
        risk_ratio_pct=(C.COL_RISK, lambda x: x.mean() * 100),
        sales=(C.COL_SALES, "sum"),
    ).reset_index()
    g["delayed_pct"] = (g["delayed"] / g["volume"] * 100).round(2)
    g["avg_gap_days"] = g["avg_gap_days"].round(3)
    g["risk_ratio_pct"] = g["risk_ratio_pct"].round(2)
    return g.sort_values("delayed_pct", ascending=False).reset_index(drop=True)


def customer_segment_analysis(df: pd.DataFrame, basis: str = "all") -> pd.DataFrame:
    d = df[~df[C.COL_CANCELED]] if basis == "delivered" else df
    g = d.groupby(C.COL_SEGMENT).agg(
        volume=(C.COL_GAP, "count"),
        delayed=(C.COL_CLASS, lambda x: int((x == "Delayed").sum())),
        risk_ratio_pct=(C.COL_RISK, lambda x: x.mean() * 100),
        sales=(C.COL_SALES, "sum"),
        avg_profit_per_order=(C.COL_PROFIT_PER_ORDER, "mean"),
    ).reset_index()
    g["delayed_pct"] = (g["delayed"] / g["volume"] * 100).round(2)
    g["risk_ratio_pct"] = g["risk_ratio_pct"].round(2)
    g["avg_profit_per_order"] = g["avg_profit_per_order"].round(2)
    g["sales"] = g["sales"].round(0)
    return g.sort_values("volume", ascending=False).reset_index(drop=True)


def financial_exposure(df: pd.DataFrame, basis: str = "all") -> dict:
    """Sales/profit ASSOCIATED with delayed shipments. 'Associated' is not
    'lost' — the dataset does not support causal loss claims."""
    d = df[~df[C.COL_CANCELED]] if basis == "delivered" else df
    delayed = d[C.COL_CLASS] == "Delayed"
    return {
        "total_sales": round(d[C.COL_SALES].sum(), 0),
        "delayed_sales": round(d.loc[delayed, C.COL_SALES].sum(), 0),
        "delayed_sales_pct": round(d.loc[delayed, C.COL_SALES].sum() / d[C.COL_SALES].sum() * 100, 2),
        "total_profit": round(d[C.COL_PROFIT_PER_ORDER].sum(), 0),
        "delayed_profit": round(d.loc[delayed, C.COL_PROFIT_PER_ORDER].sum(), 0),
    }


def mode_by_market_delay(df: pd.DataFrame, basis: str = "all") -> pd.DataFrame:
    """Delayed % pivot: Market x Shipping Mode — shows whether the mode
    pattern is global or regional."""
    d = df[~df[C.COL_CANCELED]] if basis == "delivered" else df
    piv = d.pivot_table(
        index=C.COL_MARKET,
        columns=C.COL_SHIP_MODE,
        values=C.COL_CLASS,
        aggfunc=lambda x: round((x == "Delayed").mean() * 100, 1),
    )
    return piv


def gap_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Raw distribution of the delivery delay gap (official variable)."""
    vc = df[C.COL_GAP].value_counts().sort_index()
    out = pd.DataFrame({"gap_days": vc.index, "shipments": vc.values})
    out["pct"] = (out["shipments"] / len(df) * 100).round(2)
    return out
