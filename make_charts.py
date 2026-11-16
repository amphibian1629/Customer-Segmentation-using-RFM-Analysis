import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["figure.dpi"] = 110

summary = pd.read_csv("data/segment_summary.csv").sort_values("total_revenue", ascending=True)

# Chart 1: Revenue by segment
fig, ax = plt.subplots(figsize=(8, 5))
colors = plt.cm.viridis_r([i/len(summary) for i in range(len(summary))])
ax.barh(summary["segment"], summary["total_revenue"], color=colors)
ax.set_xlabel("Total Revenue ($)")
ax.set_title("Revenue Contribution by RFM Segment")
for i, v in enumerate(summary["total_revenue"]):
    ax.text(v, i, f"  ${v:,.0f}", va="center", fontsize=8)
plt.tight_layout()
plt.savefig("charts/revenue_by_segment.png")
plt.close()

# Chart 2: Customer count vs revenue % (bubble-ish comparison)
fig, ax = plt.subplots(figsize=(8, 5))
x = range(len(summary))
ax.bar([i - 0.2 for i in x], summary["pct_of_customers"], width=0.4, label="% of Customers")
ax.bar([i + 0.2 for i in x], summary["pct_of_revenue"], width=0.4, label="% of Revenue")
ax.set_xticks(list(x))
ax.set_xticklabels(summary["segment"], rotation=30, ha="right")
ax.set_ylabel("%")
ax.set_title("Customer Share vs Revenue Share by Segment")
ax.legend()
plt.tight_layout()
plt.savefig("charts/customer_vs_revenue_share.png")
plt.close()

# Chart 3: A/B test conversion comparison
ab = pd.read_csv("data/ab_test_results.csv")
rates = ab.groupby("group")["converted"].mean().reindex(["control", "treatment"])
fig, ax = plt.subplots(figsize=(5, 5))
bars = ax.bar(rates.index, rates.values, color=["#888888", "#2a9d8f"])
ax.set_ylabel("30-Day Repurchase Rate")
ax.set_title("A/B Test: Win-Back Campaign Conversion Rate")
for bar, val in zip(bars, rates.values):
    ax.text(bar.get_x() + bar.get_width()/2, val + 0.005, f"{val:.1%}", ha="center", fontweight="bold")
plt.tight_layout()
plt.savefig("charts/ab_test_conversion.png")
plt.close()

print("Charts saved.")
