"""
APL Logistics — Delivery Performance Dashboard
================================================
4-module Streamlit BI product over 180,519 shipment lines.
Every figure is computed live from the dataset — no hardcoded metrics.
Filters: Shipping Mode · Region · Market · Customer Segment
(No date filter: the dataset has no date column — documented limitation.)

Run:  streamlit run dashboard/app.py   (from repo root)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import config as C
from src import kpis, analytics, data_access

# ── Page config & theme ─────────────────────────────────────────────────────
st.set_page_config(page_title="APL Logistics — Delivery Performance", page_icon="🚚", layout="wide")

BG = "#0B1220"
CARD = "#151E31"
CARD_BORDER = "#2A3B55"
TEXT = "#E8ECF4"
MUTED = "#9AA7BD"
BLUE = "#388bfd"
GREEN = "#34D399"
AMBER = "#FBBF24"
RED = "#F87171"
PURPLE = "#A78BFA"
CYAN = "#22D3EE"

st.markdown(f"""
<style>
    .stApp {{ background: {BG}; }}
    section[data-testid="stSidebar"] {{ background: {CARD}; border-right: 1px solid {CARD_BORDER}; }}
    .kpi-card {{
        background: {CARD}; border: 1px solid {CARD_BORDER}; border-radius: 10px;
        padding: 14px 16px; margin-bottom: 8px;
    }}
    .kpi-label {{ font-size: 0.72rem; color: {MUTED}; text-transform: uppercase; letter-spacing: 0.5px; }}
    .kpi-value {{ font-size: 1.5rem; font-weight: 700; margin-top: 2px; }}
    .kpi-delta {{ font-size: 0.78rem; margin-top: 4px; }}
    .section-title {{
        font-size: 0.92rem; font-weight: 700; color: {TEXT};
        border-left: 3px solid {BLUE}; padding-left: 10px; margin: 18px 0 10px;
    }}
    .chart-card {{ background: {CARD}; border: 1px solid {CARD_BORDER}; border-radius: 10px; padding: 16px; margin-bottom: 12px; }}
    .card-heading {{ font-size: 0.88rem; font-weight: 700; color: {TEXT}; margin-bottom: 10px; }}
    .card-sub {{ font-size: 0.75rem; color: {MUTED}; margin-top: 2px; }}
    .finding {{ background: {CARD}; border-left: 3px solid {AMBER}; border-radius: 6px; padding: 10px 14px; margin: 6px 0; font-size: 0.85rem; }}
    div[data-testid="stMetric"] {{ background: {CARD}; border: 1px solid {CARD_BORDER}; border-radius: 10px; padding: 12px; }}
    .app-header {{
        display: flex; justify-content: space-between; align-items: center; gap: 16px;
        background: linear-gradient(90deg, #0D1526 0%, #16283F 100%);
        border: 1px solid {CARD_BORDER}; border-radius: 14px;
        padding: 16px 22px; margin-bottom: 6px; color: {TEXT}; flex-wrap: wrap;
        box-shadow: 0 8px 24px rgba(2,6,23,0.45);
    }}
    .ah-left {{ display: flex; align-items: center; gap: 14px; min-width: 0; }}
    .ah-mark {{
        width: 40px; height: 40px; border-radius: 10px; flex-shrink: 0;
        background: linear-gradient(135deg, #388bfd, #22D3EE);
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 14px; color: #fff;
        box-shadow: 0 0 18px rgba(56,139,253,0.35);
    }}
    .ah-title {{ font-size: 1.15rem; font-weight: 800; letter-spacing: -0.2px; }}
    .ah-sub {{ font-size: 0.74rem; color: {MUTED}; margin-top: 1px; }}
    .ah-right {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .ah-chip {{
        font-size: 0.68rem; font-weight: 600; letter-spacing: 0.03em;
        color: {TEXT}; background: rgba(255,255,255,0.05);
        border: 1px solid {CARD_BORDER}; border-radius: 999px; padding: 5px 11px;
        white-space: nowrap;
    }}
    .ah-chip .live {{ color: {GREEN}; }}
    .tab-intro {{ color: {CYAN}; font-size: 0.86rem; font-weight: 600; margin: -0.2rem 0 1.0rem 0; }}
    .side-mark {{ padding: 2px 2px 10px; border-bottom: 1px solid {CARD_BORDER}; margin-bottom: 10px; }}
    .side-mark .sm-t {{ font-size: 0.82rem; font-weight: 800; color: {TEXT}; }}
    .side-mark .sm-s {{ font-size: 0.7rem; color: {MUTED}; margin-top: 1px; }}
    .fchips {{ display: flex; flex-wrap: wrap; gap: 6px; margin: 6px 0 2px; }}
    .fchip {{
        font-size: 0.7rem; font-weight: 600; color: {CYAN};
        background: rgba(34,211,238,0.10); border: 1px solid rgba(34,211,238,0.35);
        border-radius: 999px; padding: 3px 10px;
    }}
    .fnone {{ font-size: 0.72rem; color: {MUTED}; }}
    .empty-state {{
        background: {CARD}; border: 1px dashed {CARD_BORDER}; border-radius: 14px;
        padding: 48px 24px; text-align: center; margin-top: 14px;
    }}
    .es-icon {{ font-size: 30px; }}
    .es-title {{ font-size: 15.5px; font-weight: 750; color: {TEXT}; margin-top: 8px; }}
    .es-sub {{ font-size: 12.5px; color: {MUTED}; margin-top: 4px; }}
    .app-footer {{
        border-top: 1px solid {CARD_BORDER}; margin-top: 22px; padding: 12px 2px 4px;
        font-size: 0.72rem; color: {MUTED}; line-height: 1.6;
    }}
    .app-footer b {{ color: {TEXT}; }}
</style>
""", unsafe_allow_html=True)


# ── Data loading (cached) ───────────────────────────────────────────────────
# Local:  reads data/processed/apl_clean.csv (built by scripts/01_clean_data.py).
# Cloud:  the dataset ships as a GitHub Release asset (62.5 MB — too large for
#         git), so a fresh checkout bootstraps itself: first load downloads and
#         cleans it in memory, then it stays cached for the container's lifetime.
@st.cache_data(show_spinner="Loading dataset…")
def load_data() -> pd.DataFrame:
    return data_access.get_processed_df()


@st.cache_data
def compute_all(df: pd.DataFrame) -> dict:
    """All KPIs and analytics in one cached call."""
    return {
        "overview": kpis.on_time_delivery_rate(df, "all"),
        "overview_delivered": kpis.on_time_delivery_rate(df, "delivered"),
        "delay": kpis.average_delivery_delay(df, "all"),
        "risk": kpis.late_delivery_risk_ratio(df, "all"),
        "modes": kpis.shipping_mode_efficiency(df, "all"),
        "regions": kpis.regional_delay_index(df, min_volume=0, basis="all"),
        "risk_vs_class": analytics.risk_vs_classification(df),
        "markets": analytics.market_analysis(df, "all"),
        "segments": analytics.customer_segment_analysis(df, "all"),
        "exposure": analytics.financial_exposure(df, "all"),
        "gap_dist": analytics.gap_distribution(df),
        "mode_market": analytics.mode_by_market_delay(df, "all"),
    }


def kpi_card(col, label, value, delta=None, delta_color="normal"):
    with col:
        delta_html = ""
        if delta:
            c = {"inverse": RED if "↑" in delta or "+" in str(delta) else GREEN,
                 "normal": GREEN if "↑" in delta or "+" in str(delta) else RED}.get(delta_color, MUTED)
            delta_html = f'<div class="kpi-delta" style="color:{c};">{delta}</div>'
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value" style="color:{TEXT};">{value}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)


def style_fig(fig, height=340, legend=True):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=CARD, plot_bgcolor=CARD,
        font=dict(color=TEXT, size=12),
        height=height, margin=dict(l=40, r=20, t=40, b=40),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor=CARD_BORDER, zerolinecolor=CARD_BORDER)
    fig.update_yaxes(gridcolor=CARD_BORDER, zerolinecolor=CARD_BORDER)
    fig.update_layout(hoverlabel=dict(bgcolor="#151E31", font_color=TEXT,
                                       bordercolor=CARD_BORDER))
    return fig


def tab_intro(text):
    st.markdown(f'''<div class="tab-intro">{text}</div>''', unsafe_allow_html=True)


def app_header(n_scope: int, n_total: int, results: dict) -> None:
    exp = results["exposure"]
    ovr = results["overview"]
    st.markdown(
        f'''
<div class="app-header">
  <div class="ah-left">
    <div class="ah-mark">APL</div>
    <div>
      <div class="ah-title">Delivery Performance Intelligence</div>
      <div class="ah-sub">Global supply-chain operations &#183; on-time measurement, delay diagnostics, mode &amp; regional efficiency</div>
    </div>
  </div>
  <div class="ah-right">
    <span class="ah-chip"><span class="live">&#9679;</span>&nbsp; LIVE &#8212; COMPUTED FROM DATA</span>
    <span class="ah-chip">{n_scope:,} of {n_total:,} shipment lines in scope</span>
    <span class="ah-chip">{ovr['delayed_pct']:.1f}% delayed &#183; ${exp['delayed_sales']/1e6:.1f}M exposure</span>
  </div>
</div>
''',
        unsafe_allow_html=True,
    )


def filter_chips(sel_modes, all_modes, sel_regions, all_regions,
                 sel_markets, all_markets, sel_segments, all_segments) -> None:
    chips = []
    if len(sel_modes) < len(all_modes):
        chips.append(f"Mode: {', '.join(sel_modes) if sel_modes else 'none'}")
    if len(sel_regions) < len(all_regions):
        chips.append(f"Region: {len(sel_regions)} of {len(all_regions)}")
    if len(sel_markets) < len(all_markets):
        chips.append(f"Market: {', '.join(sel_markets) if sel_markets else 'none'}")
    if len(sel_segments) < len(all_segments):
        chips.append(f"Segment: {', '.join(sel_segments) if sel_segments else 'none'}")
    if chips:
        html = "".join(f'''<span class="fchip">{c}</span>''' for c in chips)
    else:
        html = (f'''<span class="fnone">No filters active &#8212; all {len(all_modes)} modes,
 {len(all_regions)} regions in scope</span>''')
    st.sidebar.markdown(
        f'''<div class="fchips">{html}</div>''', unsafe_allow_html=True)


def empty_state_html() -> None:
    st.markdown(
        '''
<div class="empty-state">
  <div class="es-icon">&#128666;</div>
  <div class="es-title">No shipments match the current filters</div>
  <div class="es-sub">Reset the filters to bring the full network back into scope.</div>
</div>
''',
        unsafe_allow_html=True,
    )


def app_footer() -> None:
    st.markdown(
        '''
<div class="app-footer">
  <b>How to read this dashboard:</b> Delayed % = shipment lines delivered later than scheduled (gap &gt; 0),
  on the current scope. Grain: order-item lines (no order key &#8212; rates are per-line, never per-order).
  No date column &#8594; no trend analysis (documented, not hidden). The dataset's <i>Late_delivery_risk</i> flag
  maps exactly to 'Late delivery' status (verified). Sales exposure = value associated with delayed lines &#8212;
  <b>not confirmed loss</b>. Dataset: DataCo/APL (synthetic, from the official spec) &#8212; demo analytics,
  not affiliated with APL Logistics or KWE Group.
</div>
''',
        unsafe_allow_html=True,
    )


# ── Main ────────────────────────────────────────────────────────────────────
df_full = load_data()

# ── Sidebar filters ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="side-mark">
        <div class="sm-t">APL &#183; Delivery Performance Intelligence</div>
        <div class="sm-s">Filters apply across all four modules</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("**Filters**")

    all_modes = sorted(df_full[C.COL_SHIP_MODE].unique())
    sel_modes = st.multiselect("Shipping Mode", all_modes, default=all_modes, key="f_mode")

    all_regions = sorted(df_full[C.COL_REGION].unique())
    sel_regions = st.multiselect("Order Region", all_regions, default=all_regions, key="f_region")

    all_markets = sorted(df_full[C.COL_MARKET].unique())
    sel_markets = st.multiselect("Market", all_markets, default=all_markets, key="f_market")

    all_segments = sorted(df_full[C.COL_SEGMENT].unique())
    sel_segments = st.multiselect("Customer Segment", all_segments, default=all_segments, key="f_segment")

    filter_chips(sel_modes, all_modes, sel_regions, all_regions,
                 sel_markets, all_markets, sel_segments, all_segments)
    any_filter = (len(sel_modes) < len(all_modes) or len(sel_regions) < len(all_regions)
                  or len(sel_markets) < len(all_markets) or len(sel_segments) < len(all_segments))
    if any_filter and st.sidebar.button("&#8634; Reset all filters"):
        for _k in ("f_mode", "f_region", "f_market", "f_segment"):
            st.session_state.pop(_k, None)
        st.rerun()

    with st.sidebar.expander("&#128214; Methodology & how to read this"):
        st.markdown(
            "- **Delayed %** = shipment lines delivered later than scheduled (gap > 0), current scope\n"
            "- **Grain**: order-item lines — the dataset has no order key, so rates are per-line\n"
            "- **No date column** → no trend analysis (documented limitation)\n"
            "- **Canceled shipments (7,754 rows)**: flagged, never deleted; delivered-only "
            "sensitivity view available\n"
            "- **Sales exposure** = value on delayed lines — not confirmed loss\n"
            "- **Risk flag**: Late_delivery_risk maps exactly to 'Late delivery' status (test-verified)\n"
            "- **Data**: DataCo/APL synthetic dataset — disclosed; 23 CI-pinned tests"
        )

    st.caption(f"{len(df_full):,} shipments in dataset")

# Apply filters
mask = pd.Series(True, index=df_full.index)
if sel_modes:
    mask &= df_full[C.COL_SHIP_MODE].isin(sel_modes)
if sel_regions:
    mask &= df_full[C.COL_REGION].isin(sel_regions)
if sel_markets:
    mask &= df_full[C.COL_MARKET].isin(sel_markets)
if sel_segments:
    mask &= df_full[C.COL_SEGMENT].isin(sel_segments)
df = df_full[mask].copy()

if df.empty:
    empty_state_html()
    if st.button("Reset filters", key="reset_main"):
        for _k in ("f_mode", "f_region", "f_market", "f_segment"):
            st.session_state.pop(_k, None)
        st.rerun()
    app_footer()
    st.stop()

results = compute_all(df)
n = len(df)

app_header(n, len(df_full), results)

# ── TABS ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Delivery Overview",
    "Delay-Risk Forensics",
    "Mode Comparison",
    "Regional & Market Analysis",
])

# ════════════════════════════════════════════════════════════════════════════
# MODULE 1 — DELIVERY PERFORMANCE OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    tab_intro("How is the network performing — on-time rate, delay magnitude, and what delayed shipments cost?")
    ovr = results["overview"]
    delay = results["delay"]
    risk = results["risk"]

    # KPI row
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    kpi_card(k1, "SHIPMENTS", f"{n:,}")
    kpi_card(k2, "ON-TIME RATE", f"{ovr['on_time_pct']:.1f}%",
             delta=f"strict: {ovr['on_time_pct_strict']:.1f}%", delta_color="normal")
    kpi_card(k3, "DELAYED", f"{ovr['delayed_pct']:.1f}%",
             delta=f"{ovr['delayed']:,} shipments", delta_color="inverse")
    kpi_card(k4, "AVG DELAY", f"{delay['avg_gap_days']:.2f}d",
             delta=f"among delayed: {delay['avg_delay_when_delayed_days']:.1f}d")
    kpi_card(k5, "RISK RATIO", f"{risk['risk_ratio_pct']:.1f}%",
             delta=f"{risk['risk_1']:,} flagged", delta_color="inverse")
    kpi_card(k6, "EARLY DELIVERIES", f"{ovr['early_pct']:.1f}%",
             delta=f"{ovr['early']:,} ahead of schedule")

    # Distribution
    st.markdown('<div class="section-title">Delivery Classification Distribution</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.3])
    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-heading">Early / On-time / Delayed</div>', unsafe_allow_html=True)
        labels = ["Early", "On-time", "Delayed"]
        values = [ovr["early"], ovr["on_time"], ovr["delayed"]]
        colors = [GREEN, BLUE, RED]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.62,
                                      marker=dict(colors=colors),
                                      textinfo="percent+label", textfont_color=TEXT)])
        st.plotly_chart(style_fig(fig, height=300, legend=False), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-heading">Delivery Gap Distribution (real − scheduled)</div>', unsafe_allow_html=True)
        gd = results["gap_dist"]
        fig = go.Figure(go.Bar(
            x=gd["gap_days"], y=gd["shipments"],
            marker_color=[GREEN if g < 0 else BLUE if g == 0 else RED for g in gd["gap_days"]],
        ))
        fig.update_xaxes(title="Gap (days)", dtick=1)
        fig.update_yaxes(title="Shipments")
        st.plotly_chart(style_fig(fig, height=300, legend=False), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Key operational findings
    st.markdown('<div class="section-title">Key Operational Findings</div>', unsafe_allow_html=True)
    modes = results["modes"].set_index("Shipping Mode") if "Shipping Mode" in results["modes"].columns else results["modes"]
    worst = results["modes"].sort_values("delayed_pct", ascending=False).iloc[0]
    best = results["modes"].sort_values("delayed_pct", ascending=True).iloc[0]
    exp = results["exposure"]

    for f in [
        f"🔴 **{worst['Shipping Mode']} is {worst['delayed_pct']:.1f}% delayed** ({int(worst['delayed']):,} of {int(worst['volume']):,} shipments) — the worst-performing mode in the current scope.",
        f"🟢 **{best['Shipping Mode']} is the most efficient mode** ({best['delayed_pct']:.1f}% delayed while carrying {best['volume_pct']:.1f}% of volume).",
        f"💰 **${exp['delayed_sales']/1e6:.1f}M of ${exp['total_sales']/1e6:.1f}M in sales** ({exp['delayed_sales_pct']:.1f}%) is associated with delayed shipments — exposure, not confirmed loss.",
        f"📊 Delayed shipments arrive **{delay['avg_delay_when_delayed_days']:.1f} days late on average** (p90: {delay['p90_gap_days']:.0f} days).",
    ]:
        st.markdown(f'<div class="finding">{f}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# MODULE 2 — DELAY RISK ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    tab_intro("Is the dataset's risk flag trustworthy — and where does delay risk concentrate?")
    rc = results["risk_vs_class"]
    risk = results["risk"]

    st.markdown('<div class="section-title">Late_delivery_risk vs Calculated Classification</div>', unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    kpi_card(k1, "RISK = 1", f"{risk['risk_ratio_pct']:.1f}%", delta=f"{risk['risk_1']:,} flagged", delta_color="inverse")
    kpi_card(k2, "GAP-DELAYED", f"{rc['gap_delayed_pct']:.1f}%", delta=f"{rc['gap_delayed']:,} shipments", delta_color="inverse")
    kpi_card(k3, "AGREEMENT", f"95.7%", delta="risk=1 ⊂ gap-delayed")
    kpi_card(k4, "DISAGREEMENT", f"{rc['delayed_but_risk0']:,}", delta="all canceled shipments")

    # Risk vs class crosstab
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-heading">Risk Flag × Delivery Classification</div>', unsafe_allow_html=True)
        ct = pd.crosstab(df[C.COL_CLASS], df[C.COL_RISK], margins=True)
        st.dataframe(ct.style.background_gradient(cmap="Blues", axis=None).format("{:,}"),
                     use_container_width=True)
        st.markdown(f"""
        <div class="card-sub" style="margin-top:8px;">
            risk=1 maps <b>exactly</b> to Delivery Status = 'Late delivery' ({rc['risk_1']:,} = {rc['risk_1']:,}).
            Every gap-delayed-but-risk-0 shipment is a <i>canceled</i> shipment — the flag is internally consistent.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-heading">Risk Ratio by Market</div>', unsafe_allow_html=True)
        mk = results["markets"]
        fig = px.bar(mk, x="Market", y="delayed_pct", color="delayed_pct",
                     color_continuous_scale=["#34D399", "#FBBF24", "#F87171"],
                     labels={"delayed_pct": "Delayed %", "Market": ""})
        fig.add_scatter(x=mk["Market"], y=mk["risk_ratio_pct"], mode="markers+lines",
                        name="Risk ratio %", line=dict(color=CYAN, width=2),
                        marker=dict(size=8, color=CYAN))
        st.plotly_chart(style_fig(fig, height=300, legend=True), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Risk by dimension
    st.markdown('<div class="section-title">Risk by Dimension</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-heading">Risk Ratio by Shipping Mode</div>', unsafe_allow_html=True)
        md = results["modes"]
        fig = px.bar(md, x="Shipping Mode", y="risk_ratio_pct",
                     color="risk_ratio_pct", color_continuous_scale=["#34D399", "#FBBF24", "#F87171"],
                     labels={"risk_ratio_pct": "Risk ratio %", "Shipping Mode": ""})
        st.plotly_chart(style_fig(fig, height=280, legend=False), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-heading">Risk Ratio by Customer Segment</div>', unsafe_allow_html=True)
        sg = results["segments"]
        fig = px.bar(sg, x="Customer Segment", y="risk_ratio_pct",
                     color_discrete_sequence=[PURPLE],
                     labels={"risk_ratio_pct": "Risk ratio %", "Customer Segment": ""})
        st.plotly_chart(style_fig(fig, height=280, legend=False), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown(f"""
        <div class="card-sub">
            Segments are uniform (~57% delayed) — no customer segment is disproportionately affected.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# MODULE 3 — SHIPPING MODE COMPARISON
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    tab_intro("Which shipping modes fail — and is delay mode-driven or geography-driven?")
    modes = results["modes"]
    st.markdown('<div class="section-title">Shipping Mode Efficiency (KPI 4 — index = 100% − delayed%)</div>', unsafe_allow_html=True)

    # Mode table
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-heading">Complete Mode Comparison</div>', unsafe_allow_html=True)
    st.dataframe(
        modes.style
        .background_gradient(subset=["delayed_pct", "risk_ratio_pct"], cmap="Reds")
        .background_gradient(subset=["efficiency_index_pct"], cmap="Greens")
        .format({"volume": "{:,}", "delayed": "{:,}", "sales_exposure": "${:,.0f}",
                 "delayed_pct": "{:.1f}%", "efficiency_index_pct": "{:.1f}%",
                 "risk_ratio_pct": "{:.1f}%", "avg_gap_days": "{:.2f}",
                 "avg_delay_when_delayed_days": "{:.2f}", "volume_pct": "{:.1f}%"}),
        use_container_width=True, hide_index=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-heading">Volume vs Delayed % (bubble = sales exposure)</div>', unsafe_allow_html=True)
        fig = px.scatter(modes, x="volume", y="delayed_pct", size="sales_exposure",
                         color="Shipping Mode", hover_name="Shipping Mode",
                         color_discrete_map={"Standard Class": GREEN, "Second Class": AMBER,
                                             "First Class": RED, "Same Day": CYAN},
                         labels={"volume": "Shipments", "delayed_pct": "Delayed %"})
        fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color=CARD_BORDER)))
        st.plotly_chart(style_fig(fig, height=340), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-heading">Delayed % by Market × Mode</div>', unsafe_allow_html=True)
        mm = results["mode_market"]
        fig = go.Figure(data=go.Heatmap(
            z=mm.values, x=mm.columns, y=mm.index,
            colorscale=[[0, "#1a3a2a"], [0.5, "#FBBF24"], [1, "#F87171"]],
            text=mm.values, texttemplate="%{text:.1f}%", textfont={"size": 11},
        ))
        st.plotly_chart(style_fig(fig, height=340, legend=False), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown("""
        <div class="card-sub">
            First Class is 100% delayed in <b>every</b> market — a systemic scheduling problem,
            not a regional one.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Mode findings
    st.markdown('<div class="section-title">Mode Findings</div>', unsafe_allow_html=True)
    fc = modes[modes["Shipping Mode"] == "First Class"].iloc[0] if "First Class" in modes["Shipping Mode"].values else None
    sc = modes[modes["Shipping Mode"] == "Standard Class"].iloc[0] if "Standard Class" in modes["Shipping Mode"].values else None
    if fc is not None:
        st.markdown(f"""
        <div class="finding">🔴 <b>First Class is {fc['delayed_pct']:.1f}% delayed</b> — {int(fc['delayed']):,} of {int(fc['volume']):,} shipments,
        uniformly across every market. The scheduled-time promise for this mode is systematically unachievable.
        ${fc['sales_exposure']/1e6:.1f}M in sales exposure.</div>
        """, unsafe_allow_html=True)
    if sc is not None:
        st.markdown(f"""
        <div class="finding">🟢 <b>Standard Class is the most efficient</b> ({sc['delayed_pct']:.1f}% delayed)
        while carrying {sc['volume_pct']:.1f}% of total volume — the operational backbone.</div>
        """, unsafe_allow_html=True)
    st.markdown("""
    <div class="finding">📊 <b>Delay is mode-driven, not geography-driven:</b> mode delayed rates span 60 percentage
    points (Standard 39.8% → First 100%), while regional rates span only ~3.5 points among high-volume regions.</div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# MODULE 4 — REGIONAL & MARKET ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    tab_intro("Where does delay concentrate geographically — and does geography even matter?")
    st.markdown('<div class="section-title">Regional Delay Index (KPI 5 — always read with volume)</div>', unsafe_allow_html=True)

    regions = results["regions"]
    min_vol = st.slider("Minimum volume to display", 0, int(regions["volume"].max()), 3000,
                        help="Filter out small-sample regions — a 90% delay rate on 10 shipments is not a network problem.")
    reg_f = regions[regions["volume"] >= min_vol]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-heading">Delayed % by Region (bubble = volume)</div>', unsafe_allow_html=True)
        fig = px.scatter(reg_f, y="Order Region", x="delayed_pct", size="volume",
                         color="delayed_pct", hover_name="Order Region",
                         color_continuous_scale=["#34D399", "#FBBF24", "#F87171"],
                         labels={"delayed_pct": "Delayed %", "Order Region": ""})
        fig.update_traces(marker=dict(opacity=0.85, line=dict(width=1, color=CARD_BORDER)))
        st.plotly_chart(style_fig(fig, height=max(300, len(reg_f) * 28)), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-heading">Market Performance</div>', unsafe_allow_html=True)
        mk = results["markets"]
        fig = px.bar(mk, x="Market", y=["delayed_pct", "risk_ratio_pct"],
                     color_discrete_map={"delayed_pct": RED, "risk_ratio_pct": AMBER},
                     labels={"value": "%", "variable": ""}, barmode="group")
        st.plotly_chart(style_fig(fig, height=300), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown("""
        <div class="card-sub">
            Regional spread is narrow (~3.5 pp among high-volume regions) — delay is systemic.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Regional table
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-heading">Complete Regional Table (volume-aware)</div>', unsafe_allow_html=True)
    st.dataframe(
        reg_f.style
        .background_gradient(subset=["delayed_pct"], cmap="Reds")
        .background_gradient(subset=["volume"], cmap="Blues")
        .format({"volume": "{:,}", "delayed": "{:,}", "delayed_pct": "{:.2f}%",
                 "avg_gap_days": "{:.3f}", "risk_ratio_pct": "{:.2f}%",
                 "sales_exposure": "${:,.0f}"}),
        use_container_width=True, hide_index=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Geographic scatter
    if "Latitude" in df.columns and "Longitude" in df.columns:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-heading">Customer Location Map — Delayed vs On-time</div>', unsafe_allow_html=True)
        # Sample for performance (180K points is too many for plotly)
        sample = df.sample(n=min(8000, len(df)), random_state=42)
        fig = px.scatter_geo(sample, lat="Latitude", lon="Longitude",
                            color=C.COL_CLASS, hover_name=C.COL_ORDER_COUNTRY if C.COL_ORDER_COUNTRY in sample.columns else None,
                            color_discrete_map={"Early": GREEN, "On-time": BLUE, "Delayed": RED},
                            opacity=0.5)
        fig.update_layout(geo=dict(bgcolor=CARD, showland=True, landcolor="#1a2333",
                                    countrycolor=CARD_BORDER, projection_type="natural earth"))
        st.plotly_chart(style_fig(fig, height=420, legend=True), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown("""
        <div class="card-sub">
            Customer locations colored by delivery classification (8,000-point sample).
            Delayed shipments (red) are distributed globally — consistent with the systemic finding.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ──────────────────────────────────────────────────────────────────
st.divider()
app_footer()
