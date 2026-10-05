"""KPI tests — every dashboard number pinned to the dataset."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import kpis, analytics  # noqa: E402


# ── KPI 1 ────────────────────────────────────────────────────────────────────

def test_kpi1_on_time_delivery_rate_all_basis(df):
    r = kpis.on_time_delivery_rate(df, "all")
    assert r["shipments"] == 180_519
    assert r["on_time_pct"] == 42.72          # delivered no later than scheduled
    assert r["on_time_pct_strict"] == 18.7    # exactly == scheduled
    assert r["delayed_pct"] == 57.28
    assert r["early_pct"] == 24.02


def test_kpi1_delivered_basis_stable(df):
    r = kpis.on_time_delivery_rate(df, "delivered")
    assert r["shipments"] == 180_519 - 7_754
    assert r["delayed_pct"] == 57.29          # headline rate stable across bases
    assert r["on_time_pct"] == 42.71


# ── KPI 2 ────────────────────────────────────────────────────────────────────

def test_kpi2_average_delivery_delay(df):
    r = kpis.average_delivery_delay(df, "all")
    assert r["avg_gap_days"] == 0.566         # official: mean gap, no clipping
    assert r["median_gap_days"] == 1.0
    assert r["p90_gap_days"] == 2.0
    assert r["avg_delay_when_delayed_days"] == 1.617


# ── KPI 3 ────────────────────────────────────────────────────────────────────

def test_kpi3_late_delivery_risk_ratio(df):
    r = kpis.late_delivery_risk_ratio(df, "all")
    assert r["risk_1"] == 98_977
    assert r["risk_ratio_pct"] == 54.83
    assert r["risk_0"] == 81_542


# ── KPI 4 ────────────────────────────────────────────────────────────────────

def test_kpi4_shipping_mode_efficiency(df):
    m = kpis.shipping_mode_efficiency(df).set_index("Shipping Mode")
    assert int(m.loc["First Class", "volume"]) == 27_814
    assert m.loc["First Class", "delayed_pct"] == 100.00   # every First Class shipment delayed
    assert m.loc["First Class", "efficiency_index_pct"] == 0.00
    assert m.loc["Second Class", "delayed_pct"] == 79.73
    assert m.loc["Standard Class", "delayed_pct"] == 39.77
    assert m.loc["Standard Class", "efficiency_index_pct"] == 60.23
    assert m.loc["Same Day", "delayed_pct"] == 47.83
    # volumes sum to the dataset
    assert int(m["volume"].sum()) == 180_519


def test_kpi4_all_early_shipments_are_standard_class(df):
    early = df[df["delivery_class"] == "Early"]
    assert (early["Shipping Mode"] == "Standard Class").all()
    assert len(early) == 43_366


# ── KPI 5 ────────────────────────────────────────────────────────────────────

def test_kpi5_regional_delay_index(df):
    r = kpis.regional_delay_index(df, min_volume=3000)
    top = r.iloc[0]
    assert top["Order Region"] == "Western Europe"
    assert top["delayed_pct"] == 58.52
    assert int(top["volume"]) == 27_109
    # regional spread is narrow — systemic, not regional
    assert (r["delayed_pct"].max() - r["delayed_pct"].min()) < 4.0


# ── Risk vs classification (key analytical finding) ─────────────────────────

def test_risk_vs_classification(df):
    rc = analytics.risk_vs_classification(df)
    assert rc["both_delayed_and_risk1"] == 98_977
    assert rc["delayed_but_risk0"] == 4_423
    assert rc["delayed_but_risk0_status_breakdown"] == {"Shipping canceled": 4_423}
    assert rc["risk1_equals_late_delivery_status"] is True


def test_market_analysis(df):
    m = analytics.market_analysis(df).set_index("Market")
    assert int(m.loc["Europe", "volume"]) == 50_252
    assert m.loc["Europe", "delayed_pct"] == 57.69


def test_customer_segments_uniform(df):
    s = analytics.customer_segment_analysis(df).set_index("Customer Segment")
    # no segment disproportionately affected: all within 0.5pp of 57.3
    for seg in ("Consumer", "Corporate", "Home Office"):
        assert abs(s.loc[seg, "delayed_pct"] - 57.3) < 0.5


def test_financial_exposure(df):
    f = analytics.financial_exposure(df)
    assert f["delayed_sales"] == 21_025_185
    assert f["delayed_sales_pct"] == 57.16
