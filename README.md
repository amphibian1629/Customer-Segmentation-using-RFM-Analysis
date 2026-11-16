# Customer Analytics Pipeline: RFM Segmentation → A/B Test

An end-to-end customer analytics workflow that goes from raw transaction
data to a **tested, statistically validated business recommendation** — the
same loop a data analyst runs in production: segment the customer base,
identify a high-priority group, design an intervention, and measure whether
it actually worked.

## Why these two projects are combined

They are not two independent case studies — the second is a direct
consequence of the first. RFM segmentation surfaces *which* customers to
act on (the "At Risk" segment); the A/B test answers *whether the action
worked*, with a real hypothesis test rather than a gut-feel recommendation.
Doing both end-to-end demonstrates the full analyst loop: **describe →
prioritize → intervene → validate**, not just an isolated chart or model.

For the SQL methodology, scoring logic, and segmentation results, see
[`README_RFM.md`](README_RFM.md). For the experiment design, statistical
test, and results, see [`README_AB_TEST.md`](README_AB_TEST.md). This file
only covers what those two don't.

## Repo Structure

```
abtest_rfmsegment/
├── generate_data.py       # builds the synthetic transactions dataset
├── rfm_segmentation.py    # SQL-based RFM scoring + segment assignment
├── ab_test.py             # simulates + statistically tests the win-back campaign
├── make_charts.py         # generates all chart images
├── charts/                # output visualizations
├── data/                  # output CSVs (transactions, segments, test results)
├── README_RFM.md          # RFM methodology + results
└── README_AB_TEST.md      # A/B test methodology + results
```

## How to Run

Scripts must be run in order — each stage depends on the previous stage's
output:

```bash
pip install pandas numpy scipy matplotlib

python generate_data.py        # → data/transactions.csv
python rfm_segmentation.py     # → data/rfm_segments.csv, segment_summary.csv
python ab_test.py              # → data/ab_test_results.csv (uses the "At Risk" segment)
python make_charts.py          # → charts/*.png
```

## A Note on the Data

The transaction data is synthetically generated (`generate_data.py`), not
sourced from a real company, since no proprietary dataset was available.
It was deliberately built with heterogeneous customer behavior patterns
(varying order frequency, recency, and spend across simulated customer
types) so that the resulting segmentation and experiment produce a
genuine, non-trivial signal rather than an artificially clean result.

## Tech Stack

SQL (SQLite, window functions), Python (pandas, NumPy, SciPy), Matplotlib
