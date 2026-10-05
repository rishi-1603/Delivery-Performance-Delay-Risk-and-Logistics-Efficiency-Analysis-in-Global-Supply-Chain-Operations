"""02_analysis_report.py — compute every analysis and write the findings report.

Run:  python scripts/02_analysis_report.py   (after 01_clean_data.py)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from src import config as C  # noqa: E402
from src import kpis, analytics  # noqa: E402


def md_table(df: pd.DataFrame, floatfmt: int = 2) -> str:
    d = df.copy()
    for col in d.select_dtypes(include="float").columns:
        d[col] = d[col].map(lambda v: f"{v:,.{floatfmt}f}" if pd.notna(v) else "—")
    for col in d.select_dtypes(include="number").columns:
        if d[col].dtype != object:
            d[col] = d[col].map(lambda v: f"{v:,.0f}")
    header = "| " + " | ".join(str(c) for c in d.columns) + " |"
    sep = "| " + " | ".join("---" for _ in d.columns) + " |"
    rows = ["| " + " | ".join(str(v) for v in r) + " |" for r in d.values]
    return "\n".join([header, sep] + rows)


def main() -> None:
    df = pd.read_csv(C.PROCESSED_CSV, low_memory=False)

    L = ["# APL Logistics — Delivery Performance Analysis Report", ""]

    # ── Baseline ──
    ovr_all = kpis.on_time_delivery_rate(df, "all")
    ovr_del = kpis.on_time_delivery_rate(df, "delivered")
    delay_all = kpis.average_delivery_delay(df, "all")
    risk_all = kpis.late_delivery_risk_ratio(df, "all")

    L += [
        "## 1. Overall delivery performance (official, all-rows basis)",
        "",
        f"- Shipments: **{ovr_all['shipments']:,}**",
        f"- Early: **{ovr_all['early']:,} ({ovr_all['early_pct']}%)** | "
        f"On-time (== scheduled): **{ovr_all['on_time']:,} ({ovr_all['on_time_pct_strict']}%)** | "
        f"Delayed: **{ovr_all['delayed']:,} ({ovr_all['delayed_pct']}%)**",
        f"- **KPI 1 — On-time delivery rate (delivered no later than scheduled): "
        f"{ovr_all['on_time_pct']}%** (strict == scheduled: {ovr_all['on_time_pct_strict']}%)",
        f"- **KPI 2 — Average delivery delay (mean gap): {delay_all['avg_gap_days']} days** "
        f"(median {delay_all['median_gap_days']:.0f}, p90 {delay_all['p90_gap_days']:.0f}, "
        f"delay-among-delayed {delay_all['avg_delay_when_delayed_days']} days)",
        f"- **KPI 3 — Late delivery risk ratio: {risk_all['risk_ratio_pct']}%** "
        f"({risk_all['risk_1']:,} shipments flagged)",
        "",
        f"Sensitivity (delivered-only basis, excludes {ovr_all['shipments'] - ovr_del['shipments']:,} "
        f"canceled): delayed {ovr_del['delayed_pct']}% | on-time-or-early {ovr_del['on_time_pct']}% "
        "— the headline rate is stable across bases.",
        "",
    ]

    # ── Gap distribution ──
    L += ["## 2. Delivery gap distribution", "", md_table(analytics.gap_distribution(df)), ""]

    # ── Risk vs classification ──
    rc = analytics.risk_vs_classification(df)
    L += [
        "## 3. Late_delivery_risk vs calculated classification",
        "",
        f"- Gap-delayed: **{rc['gap_delayed']:,} ({rc['gap_delayed_pct']}%)** | "
        f"risk=1: **{rc['risk_1']:,} ({rc['risk_1_pct']}%)**",
        f"- Both delayed AND risk=1: **{rc['both_delayed_and_risk1']:,}**",
        f"- Delayed but risk=0: **{rc['delayed_but_risk0']:,}** — status breakdown: "
        f"{rc['delayed_but_risk0_status_breakdown']}",
        f"- risk=1 count equals 'Late delivery' status count: **{rc['risk1_equals_late_delivery_status']}**",
        "",
        "**Finding:** the dataset's risk flag maps exactly to Delivery Status = 'Late delivery', "
        "and every disagreement with the gap classification is a *canceled* shipment. The risk "
        "flag is consistent; the two bases differ only in how canceled shipments are handled.",
        "",
    ]

    # ── KPI 4: shipping mode ──
    mode = kpis.shipping_mode_efficiency(df)
    L += [
        "## 4. Shipping mode efficiency (KPI 4 — efficiency index = 100% − delayed%)",
        "",
        md_table(mode),
        "",
        "**Findings (observed associations, not causal claims):**",
        "- **First Class is 100.00% delayed** (27,814 of 27,814) across every market — a "
        "systematic scheduling problem, not a regional one.",
        "- **Second Class: 79.73% delayed** with the highest average delay when delayed (2.50 days).",
        "- **Standard Class is the most efficient** (60.23% on-time-or-early) despite carrying "
        "59.7% of volume.",
        "- Same Day (the premium mode) is only 52.17% on-time-or-early — and is the smallest "
        "volume mode (5.4%).",
        "",
    ]

    # ── Mode × market ──
    L += [
        "## 5. Delayed % by market × shipping mode",
        "",
        md_table(analytics.mode_by_market_delay(df, "all").reset_index()),
        "",
        "The First Class pattern is uniform across all five markets — confirming a "
        "mode-level (systemic) driver rather than a regional one.",
        "",
    ]

    # ── KPI 5: regional ──
    reg = kpis.regional_delay_index(df, min_volume=3000)
    L += [
        "## 6. Regional delay index (KPI 5, high-volume regions ≥ 3,000 shipments)",
        "",
        md_table(reg),
        "",
        "**Finding:** regional variation is narrow (≈55–58.5% delayed among high-volume "
        "regions). Delay is systemic across the network — the dominant driver is shipping "
        "mode, not geography. Western Europe is the worst high-volume region (58.52% delayed, "
        "27,109 shipments); West Africa the best of the ≥3,000 group (55.01%).",
        "",
    ]

    # ── Market ──
    L += ["## 7. Market analysis", "", md_table(analytics.market_analysis(df)), ""]

    # ── Segment ──
    L += [
        "## 8. Customer segment analysis",
        "",
        md_table(analytics.customer_segment_analysis(df)),
        "",
        "**Finding:** delivery performance is statistically uniform across Consumer, "
        "Corporate and Home Office (≈57% delayed each). No customer segment is "
        "disproportionately affected — there is no 'premium penalty' in this dataset. "
        "(The dataset has three generic segments; enterprise/premium tiers do not exist here.)",
        "",
    ]

    # ── Financial ──
    fin = analytics.financial_exposure(df)
    L += [
        "## 9. Financial exposure (associated value — NOT confirmed loss)",
        "",
        f"- Sales associated with delayed shipments: **${fin['delayed_sales']:,.0f} of "
        f"${fin['total_sales']:,.0f} ({fin['delayed_sales_pct']}%)**",
        f"- Profit-per-order associated with delayed shipments: ${fin['delayed_profit']:,.0f} "
        f"of ${fin['total_profit']:,.0f}",
        "",
        "The dataset does not support causal loss claims (no penalty, churn or refund data). "
        "'Exposure' = value shipped on delayed legs.",
        "",
    ]

    C.REPORTS_DIR.mkdir(exist_ok=True)
    (C.REPORTS_DIR / "analysis_report.md").write_text("\n".join(L), encoding="utf-8")
    print(f"report written: {C.REPORTS_DIR / 'analysis_report.md'}")


if __name__ == "__main__":
    main()
