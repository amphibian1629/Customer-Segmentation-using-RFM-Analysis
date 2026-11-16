"""
Customer Segmentation using RFM (Recency, Frequency, Monetary) Analysis
------------------------------------------------------------------------
All scoring logic is done in SQL (SQLite) using window functions (NTILE),
exactly as it would be done in PostgreSQL/Snowflake in production.
"""
import sqlite3
import pandas as pd

conn = sqlite3.connect(":memory:")
tx = pd.read_csv("data/transactions.csv", parse_dates=["order_date"])
tx.to_sql("transactions", conn, index=False, if_exists="replace")

SNAPSHOT_DATE = "2026-01-01"  # "today" for recency calculation

# ---------------------------------------------------------------
# STEP 1: Compute raw RFM metrics per customer (pure SQL)
# ---------------------------------------------------------------
raw_rfm_sql = f"""
SELECT
    customer_id,
    CAST(julianday('{SNAPSHOT_DATE}') - julianday(MAX(order_date)) AS INTEGER) AS recency_days,
    COUNT(order_id) AS frequency,
    ROUND(SUM(order_value), 2) AS monetary
FROM transactions
GROUP BY customer_id
"""
raw_rfm = pd.read_sql(raw_rfm_sql, conn)
raw_rfm.to_sql("raw_rfm", conn, index=False, if_exists="replace")

# ---------------------------------------------------------------
# STEP 2: Score each customer 1-5 on R, F, M using NTILE window functions
#   - Recency: lower days-since-last-order = better -> score 5 = most recent
#   - Frequency / Monetary: higher = better -> score 5 = highest
# ---------------------------------------------------------------
scoring_sql = """
SELECT
    customer_id,
    recency_days,
    frequency,
    monetary,
    (6 - NTILE(5) OVER (ORDER BY recency_days ASC))  AS r_score,
    NTILE(5) OVER (ORDER BY frequency ASC)           AS f_score,
    NTILE(5) OVER (ORDER BY monetary ASC)            AS m_score
FROM raw_rfm
"""
scored = pd.read_sql(scoring_sql, conn)
scored["rfm_score"] = scored["r_score"] + scored["f_score"] + scored["m_score"]
scored.to_sql("rfm_scored", conn, index=False, if_exists="replace")

# ---------------------------------------------------------------
# STEP 3: Segment customers into tiers based on R/F/M score combinations
#   (business rules layered on top of the SQL-computed scores)
# ---------------------------------------------------------------
def segment(row):
    r, f, m = row["r_score"], row["f_score"], row["m_score"]
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif r >= 3 and f >= 3:
        return "Loyal Customers"
    elif r >= 4 and f <= 2:
        return "New / Promising"
    elif r <= 2 and f >= 4:
        return "At Risk"
    elif r <= 2 and f >= 2 and m >= 3:
        return "Cant Lose Them"
    elif r <= 2 and f <= 2:
        return "Hibernating / Lost"
    else:
        return "Needs Attention"

scored["segment"] = scored.apply(segment, axis=1)
scored.to_csv("data/rfm_segments.csv", index=False)

# ---------------------------------------------------------------
# STEP 4: Segment-level summary (pure SQL aggregation)
# ---------------------------------------------------------------
scored.to_sql("rfm_final", conn, index=False, if_exists="replace")
summary_sql = """
SELECT
    segment,
    COUNT(*) AS customer_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM rfm_final), 1) AS pct_of_customers,
    ROUND(SUM(monetary), 2) AS total_revenue,
    ROUND(100.0 * SUM(monetary) / (SELECT SUM(monetary) FROM rfm_final), 1) AS pct_of_revenue,
    ROUND(AVG(monetary), 2) AS avg_customer_value,
    ROUND(AVG(recency_days), 0) AS avg_recency_days
FROM rfm_final
GROUP BY segment
ORDER BY total_revenue DESC
"""
summary = pd.read_sql(summary_sql, conn)
summary.to_csv("data/segment_summary.csv", index=False)

print(summary.to_string(index=False))
print()
total_customers = len(scored)
top2 = summary.sort_values("total_revenue", ascending=False).head(2)
top2_cust_pct = top2["pct_of_customers"].sum()
top2_rev_pct = top2["pct_of_revenue"].sum()
print(f"Total customers: {total_customers}")
print(f"Champions + Loyal Customers = {top2_cust_pct:.1f}% of customers driving {top2_rev_pct:.1f}% of revenue")
