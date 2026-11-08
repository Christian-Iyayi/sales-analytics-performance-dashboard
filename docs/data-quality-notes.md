# Data quality notes

This document records where the numbers in this repository come from, how they were verified, and
what remains uncertain. It exists because a dashboard is only as trustworthy as its reconciliation
trail.

---

## 1. Provenance

| Item | Detail |
| --- | --- |
| Original publication | [Sales Analytics Performance Dashboard](https://medium.com/@krisnice2002gmail.com/sales-analytics-performance-dashboard-316c17710990), Medium, Christian Iyayi |
| Source artefacts | Five screenshots published with the article, preserved unmodified in [`images/`](../images) |
| Extraction method | Screenshots read at 4× magnification; every figure transcribed manually, then validated arithmetically |
| Period | January – March 2024 |
| Records in scope | 50 |
| Published grand totals | Revenue **$112,600** · Units **420** · Category shares **100.00%** |

The five source artefacts are:

1. `01-data-extract.png` — record-level extract with date, day, region, salesperson, product,
   category, units, unit price and total sales.
2. `02-region-salesperson-category-pivots.png` — revenue by region, revenue by salesperson, units by
   product, category share.
3. `03-units-monthly-daily-pivots.png` — units by region × salesperson, monthly revenue, daily
   revenue, product revenue.
4. `04-product-revenue-per-unit-pivots.png` — product revenue and revenue per unit.
5. `05-dashboard-overview.png` — the finished single-page dashboard with KPI cards.

---

## 2. Verification rules

Every transcribed table had to pass four independent tests before being committed:

**Rule 1 — Grand total.** Each cut (region, salesperson, product, category, month, day) must sum to
**$112,600**, the figure printed in every grand-total row and in the dashboard KPI card.

**Rule 2 — Unit total.** Each cut must sum to **420 units**, and the region × salesperson matrix must
sum to 420 on both axes.

**Rule 3 — Price identity.** For every product line, `units × unit price = revenue`. This is the
strongest available check because it constrains three numbers at once.

**Rule 4 — Dashboard agreement.** The KPI cards and chart tooltips on `05-dashboard-overview.png`
must agree with the pivot tables. Where a low-resolution digit was ambiguous, the dashboard figure
decided it.

All four rules are enforced in code by
[`analysis/build_tables.py`](../analysis/build_tables.py), which exits with an error rather than
writing a table that fails.

---

## 3. Reconciliation trail

Screenshots of pivot tables are easy to misread at native resolution — a `26,750` can look like
`28,750`, and a `21,500` like `21,600`. Each ambiguity was resolved by testing which candidate value
satisfies Rules 1–4. The resolutions are recorded below.

### 3.1 Region revenue

| Candidate reading | Sum of regions | Rule 1 verdict |
| --- | ---: | --- |
| East 34,700 · North 33,670 · West 28,750 · South 17,480 | 114,610 | Fails |
| East 34,700 · North 33,670 · West **26,750** · South 17,480 | **112,600** | Passes |

**Adopted:** West = **$26,750**, confirmed independently by the West bar in the dashboard's region
chart and by the $214/unit implied for 125 units.

### 3.2 Product revenue

| Product | Units | Unit price | Units × price | Adopted revenue |
| --- | ---: | ---: | ---: | ---: |
| Laptop | 66 | $700 | $46,200 | $46,200 |
| Smartphone | 43 | $500 | **$21,500** | $21,500 |
| Desk | 55 | $200 | $11,000 | $11,000 |
| Monitor | 30 | $250 | $7,500 | $7,500 |
| Tablet | 24 | $300 | $7,200 | $7,200 |
| Headphones | 68 | $80 | $5,440 | $5,440 |
| Bookshelf | 43 | $120 | $5,160 | $5,160 |
| Office Chair | 43 | $100 | $4,300 | $4,300 |
| Printer | 19 | $150 | $2,850 | $2,850 |
| Keyboard | 29 | $50 | $1,450 | $1,450 |
| **Total** | **420** | | | **$112,600** |

Two lines carried the most ambiguity:

- **Smartphone.** A reading of `21,600` would break both Rule 3 (43 × $500 = $21,500) and Rule 1
  (product total becomes $112,700). **$21,500 adopted.**
- **Desk.** The published article itself notes that an earlier transcription of $10,100 was
  reconciled to **$11,000** to align with 55 units at an average unit price of $200. **$11,000
  adopted**, consistent with both rules.

### 3.3 Units by product

| Product | Units |
| --- | ---: |
| Headphones | 68 |
| Laptop | 66 |
| Desk | 55 |
| Office Chair | 43 |
| Smartphone | 43 |
| Bookshelf | 43 |
| Monitor | 30 |
| Keyboard | 29 |
| Tablet | 24 |
| Printer | 19 |
| **Total** | **420** |

Earlier readings of Keyboard = 23 and Tablet = 19 produced a total of 409 units, contradicting the
published 420. At 4× magnification the values are **29** and **24**, and they reconcile exactly.
**420 adopted.**

### 3.4 Salesperson revenue

| Salesperson | Revenue | Units | Revenue per unit | Share |
| --- | ---: | ---: | ---: | ---: |
| Michael Brown | $39,660 | 131 | $302.75 | 35.2% |
| Emily Davis | $24,410 | 63 | $387.46 | 21.7% |
| John Doe | $23,850 | 120 | $198.75 | 21.2% |
| Jane Smith | $14,290 | 61 | $234.26 | 12.7% |
| Chris Taylor | $10,390 | 45 | $230.89 | 9.2% |
| **Total** | **$112,600** | **420** | **$268.10** | **100%** |

Michael Brown's $39,660 was checked against three independent facts: the required grand total, his
131 units, and the published note that he is the top performer. A lower transcription would leave
$112,600 unreachable given the other four figures.

### 3.5 Time cuts

| Cut | Values | Sum |
| --- | --- | ---: |
| Month | Jan 73,500 · Feb 32,600 · Mar 6,500 | $112,600 |
| Day | Mon 9,200 · Tue 29,590 · Wed 6,850 · Thu 25,200 · Fri 17,010 · Sat 16,950 · Sun 7,800 | $112,600 |

Both cascades reconcile at high magnification, which is why the tables are published here in full.

---

## 4. Known limitations

1. **Incomplete record-level data.** The published extract screenshot shows **26 of the 50 records**.
   `data/transactions_sample.csv` preserves those 26 rows for schema documentation only; it is not
   used for any aggregate, and its total ($64,670) is **not** comparable to the quarter total.

2. **Aggregates only.** All analysis runs on pre-aggregated pivot values. Cross-tabs that were never
   published — for example product × region, or salesperson × product — cannot be reconstructed.

3. **No cost, margin or order count.** Profitability and average order value cannot be computed.
   Recommendation 6.4 (assortment review) is explicitly blocked on this data gap.

4. **Time-series fragility.** March is only $6,500 across the quarter. Whether that reflects genuine
   demand collapse, pipeline timing, or incomplete records for the month is not determinable from
   the published material. The report therefore treats all month- and day-based findings as
   **hypotheses to test**, not conclusions.

5. **Small sample.** 50 records, five salespeople, one quarter. Rankings are sensitive to individual
   large deals: a single $10,500 Laptop order is 9.3% of quarterly revenue on its own.

6. **No statistical testing.** Percentages are descriptive shares, not estimates with confidence
   intervals. No significance claims are made anywhere in this repository.

---

## 5. How to resolve the open items

| Open item | Required input | Owner |
| --- | --- | --- |
| Full 50-record extract | Original workbook, unredacted | Data owner |
| Margin analysis | Cost per unit or COGS by line | Finance |
| Order-level behaviour | Order ID / invoice number | Sales ops |
| March completeness | Daily ledger for March 2024 | Finance |
| Territory context | Region size, headcount, account lists | Sales leadership |

Until these are available, the conclusions in this repository should be read as **directional
rankings of a single quarter**, which is precisely how the original analysis framed them.
