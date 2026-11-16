"""
Generates a synthetic but realistic e-commerce transactions dataset,
mimicking the structure of the classic "Online Retail II" dataset:
one row per order-line, with customer_id, order_date, and revenue.

Design choices to make RFM segmentation meaningful:
- ~4,000 customers with heterogeneous behavior (some frequent/big spenders,
  some one-time small buyers, some who used to buy but have gone quiet).
- Orders spread over a 24-month window (2024-01-01 to 2025-12-31).
- Customer "archetypes" drive realistic Recency/Frequency/Monetary spread.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

N_CUSTOMERS = 4000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31)
TOTAL_DAYS = (END_DATE - START_DATE).days

# Customer archetypes: (share of customers, order_count_range, avg_order_value_range, recency_bias)
# recency_bias: 'active' = recent orders more likely, 'churned' = orders concentrated early, 'mixed' = uniform
archetypes = [
    dict(name="champion",      share=0.08, orders=(15, 40), aov=(60, 220),  recency="active"),
    dict(name="loyal",         share=0.17, orders=(6, 14),  aov=(40, 150),  recency="active"),
    dict(name="potential",     share=0.20, orders=(3, 6),   aov=(30, 120),  recency="mixed"),
    dict(name="at_risk",       share=0.20, orders=(4, 10),  aov=(50, 180),  recency="churned"),
    dict(name="hibernating",   share=0.20, orders=(2, 4),   aov=(20, 90),   recency="churned"),
    dict(name="one_timer",     share=0.15, orders=(1, 1),   aov=(15, 80),   recency="mixed"),
]

rows = []
customer_id = 100000

for arc in archetypes:
    n = int(N_CUSTOMERS * arc["share"])
    for _ in range(n):
        customer_id += 1
        n_orders = np.random.randint(arc["orders"][0], arc["orders"][1] + 1)
        aov_mu = np.random.uniform(arc["aov"][0], arc["aov"][1])

        if arc["recency"] == "active":
            # orders skew toward the recent 6 months
            order_days = np.clip(
                np.random.normal(loc=TOTAL_DAYS - 80, scale=120, size=n_orders), 0, TOTAL_DAYS
            )
        elif arc["recency"] == "churned":
            # orders concentrated in the first 12 months, none recently
            order_days = np.clip(
                np.random.normal(loc=TOTAL_DAYS * 0.30, scale=100, size=n_orders), 0, TOTAL_DAYS * 0.75
            )
        else:  # mixed
            order_days = np.random.uniform(0, TOTAL_DAYS, size=n_orders)

        for od in order_days:
            order_date = START_DATE + timedelta(days=float(od))
            order_value = max(5, np.random.normal(loc=aov_mu, scale=aov_mu * 0.35))
            rows.append((customer_id, order_date.strftime("%Y-%m-%d"), round(order_value, 2), arc["name"]))

df = pd.DataFrame(rows, columns=["customer_id", "order_date", "order_value", "_true_archetype"])
df = df.sort_values(["customer_id", "order_date"]).reset_index(drop=True)
df["order_id"] = ["ORD" + str(100000 + i) for i in range(len(df))]

# Save full transactions (keep true archetype hidden in a separate file for our own validation only)
df[["order_id", "customer_id", "order_date", "order_value"]].to_csv("data/transactions.csv", index=False)
df[["customer_id", "_true_archetype"]].drop_duplicates().to_csv("data/_customer_archetypes_reference.csv", index=False)

print(f"Customers generated: {df['customer_id'].nunique()}")
print(f"Total transactions: {len(df)}")
print(f"Total revenue: ${df['order_value'].sum():,.2f}")
print(f"Date range: {df['order_date'].min()} to {df['order_date'].max()}")
