# LinkedIn Post — APL Logistics Delivery Analytics

## Title
🚚 I analyzed 180,519 shipment lines to find out why half the world's deliveries are late — and the answer isn't geography.

## Description

Most "delivery analytics" dashboards show you charts. I wanted to build one that tells an operations team exactly what to fix.

That project is now live: APL Logistics Delivery Performance Analytics — on-time measurement, delay diagnostics, and mode-efficiency analysis across 180,519 shipment lines in 23 regions, 5 markets, and 4 shipping modes.

🎯 The business problem
Delivery delays → SLA violations and penalties. But the organization had no clear on-time measurement, no understanding of *why* shipments are late, and no visibility into which modes or regions are high-risk.

📊 What I found (all verified and test-pinned)
• 57.28% of shipments are delayed — $21.0M of $36.8M in sales rides on delayed legs
• 🔴 First Class shipping is 100.00% delayed — 27,814 of 27,814 shipments, in every single market
• Delay is mode-driven, not geography-driven: mode rates span 60 percentage points, regional rates only 3.5
• The dataset's late_delivery_risk flag maps exactly to 'Late delivery' status — I verified every disagreement is a canceled shipment
• No customer segment is disproportionately affected (all ~57% delayed)

🧠 The analyst mindset
The most valuable insight isn't a chart — it's the redirect: stop regional firefighting, fix the mode-scheduling policy. First Class isn't underperforming; it's making a promise that can't be kept.

🛠️ What I built
• KPI engine: 5 official KPIs (on-time rate, avg delay, risk ratio, mode efficiency, regional index)
• Streamlit dashboard: 4 modules with cross-filtering (mode, region, market, segment)
• SQL layer: schema + all KPIs + diagnostics (SQLite & PostgreSQL compatible), mirroring Python exactly — every query reconciled against the Python engine
• 23 automated tests: every headline number pinned to the dataset
• Full documentation: data dictionary, KPI dictionary, methodology, research paper

🔗 GitHub: https://github.com/rishi-1603/Delivery-Performance-Delay-Risk-and-Logistics-Efficiency-Analysis-in-Global-Supply-Chain-Operations

I'm a 2026 Data Science graduate seeking Data Analyst / Operations Analyst / BI Analyst opportunities.

Supply chain and analytics folks — what's the first thing you'd investigate: carrier performance, mode scheduling, or regional capacity?

#SupplyChainAnalytics #DataAnalytics #Logistics #SQL #Python #Streamlit #OperationsResearch
