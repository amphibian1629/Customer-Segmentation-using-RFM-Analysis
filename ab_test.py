"""
A/B Test: Win-Back Campaign Lift on "At Risk" Customer Segment
-----------------------------------------------------------------
Business question: does a targeted win-back email (15% discount code)
increase repurchase rate among customers the RFM model flagged as "At Risk"?

Design:
  - Population: all customers in the "At Risk" RFM segment.
  - Random 50/50 split into Treatment (received win-back email) vs Control (no email).
  - Outcome metric: whether the customer placed a new order within 30 days.
  - True underlying lift is simulated (control ~11% baseline repurchase rate,
    treatment ~19% due to the discount) to mimic a realistic marketing effect size.
Analysis:
  - Two-proportion z-test for statistical significance
  - 95% confidence interval on the difference in conversion rates
"""
import numpy as np
import pandas as pd
from scipy import stats

np.random.seed(7)

rfm = pd.read_csv("data/rfm_segments.csv")
at_risk = rfm[rfm["segment"] == "At Risk"].copy()
n = len(at_risk)

# Random assignment
at_risk["group"] = np.random.choice(["treatment", "control"], size=n, p=[0.5, 0.5])

# Simulate true conversion behavior (30-day repurchase after campaign)
TRUE_CONTROL_RATE = 0.11
TRUE_TREATMENT_RATE = 0.19

at_risk["converted"] = at_risk.apply(
    lambda row: np.random.binomial(1, TRUE_TREATMENT_RATE if row["group"] == "treatment" else TRUE_CONTROL_RATE),
    axis=1,
)

at_risk[["customer_id", "group", "converted"]].to_csv("data/ab_test_results.csv", index=False)

# ---------------------------------------------------------------
# Two-proportion z-test
# ---------------------------------------------------------------
grp = at_risk.groupby("group")["converted"].agg(["sum", "count"])
x1, n1 = grp.loc["treatment", "sum"], grp.loc["treatment", "count"]   # treatment
x2, n2 = grp.loc["control", "sum"], grp.loc["control", "count"]       # control

p1, p2 = x1 / n1, x2 / n2
p_pool = (x1 + x2) / (n1 + n2)
se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
z_stat = (p1 - p2) / se_pool
p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

# 95% CI on the difference (unpooled SE, standard for CI)
se_diff = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
diff = p1 - p2
ci_low, ci_high = diff - 1.96 * se_diff, diff + 1.96 * se_diff

relative_lift = (p1 - p2) / p2 * 100

print("=== A/B Test: Win-Back Campaign on 'At Risk' Segment ===")
print(f"Sample size: {n} customers ({n1} treatment / {n2} control)")
print(f"Treatment conversion rate: {p1:.2%} ({x1}/{n1})")
print(f"Control conversion rate:   {p2:.2%} ({x2}/{n2})")
print(f"Absolute lift: {diff:.2%}  |  Relative lift: {relative_lift:.1f}%")
print(f"Z-statistic: {z_stat:.3f}")
print(f"P-value: {p_value:.4f}")
print(f"95% CI on difference: [{ci_low:.2%}, {ci_high:.2%}]")
print(f"Statistically significant at alpha=0.05: {p_value < 0.05}")

# Save summary
with open("data/ab_test_summary.txt", "w") as f:
    f.write("A/B Test Summary: Win-Back Campaign on At-Risk Segment\n")
    f.write(f"Sample size: {n} ({n1} treatment / {n2} control)\n")
    f.write(f"Treatment conversion: {p1:.2%}\nControl conversion: {p2:.2%}\n")
    f.write(f"Absolute lift: {diff:.2%}\nRelative lift: {relative_lift:.1f}%\n")
    f.write(f"Z-statistic: {z_stat:.3f}\nP-value: {p_value:.4f}\n")
    f.write(f"95% CI: [{ci_low:.2%}, {ci_high:.2%}]\n")
    f.write(f"Significant at 0.05: {p_value < 0.05}\n")
