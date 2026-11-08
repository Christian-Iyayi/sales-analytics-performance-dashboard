"""Build the analysis-ready tables for the Sales Analytics Performance Dashboard.

The inputs in this module are the aggregate figures transcribed directly from the
source pivot tables and the Excel dashboard published with the report. The script
recomputes derived fields (revenue per unit, share of revenue) and validates that
every table reconciles to the published grand total of $112,600 and 420 units.

Run from the repository root:

    python analysis/build_tables.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

TOTAL_REVENUE = 112_600
TOTAL_UNITS = 420
TOTAL_RECORDS = 50

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# --- Source aggregates -------------------------------------------------------
# Revenue by region (source: "TOTAL REVENUE REGION" pivot)
REGIONS = [("East", 34_700), ("North", 33_670), ("West", 26_750), ("South", 17_480)]

# Units by region and salesperson (source: "UNIT SOLD BY REGION AND SALESPERSON"
# matrix, columns ordered East, North, South, West)
UNITS_MATRIX = [
    # salesperson, East, North, South, West
    ("Michael Brown", 35, 15, 13, 68),
    ("John Doe", 24, 29, 34, 33),
    ("Emily Davis", 1, 38, 18, 6),
    ("Jane Smith", 29, 0, 26, 6),
    ("Chris Taylor", 13, 18, 2, 12),
]

# Revenue by salesperson (source: "TOP PERFORMING SALESPERSON BY REVENUE" pivot)
SALESPEOPLE = [
    ("Michael Brown", 39_660),
    ("Emily Davis", 24_410),
    ("John Doe", 23_850),
    ("Jane Smith", 14_290),
    ("Chris Taylor", 10_390),
]

# Revenue by product (source: "PRODUCT REVENUE" pivot)
PRODUCTS = [
    # product, category, unit price, units, revenue
    ("Laptop", "Electronics", 700, 66, 46_200),
    ("Smartphone", "Electronics", 500, 43, 21_500),
    ("Desk", "Furniture", 200, 55, 11_000),
    ("Monitor", "Electronics", 250, 30, 7_500),
    ("Tablet", "Electronics", 300, 24, 7_200),
    ("Headphones", "Electronics", 80, 68, 5_440),
    ("Bookshelf", "Furniture", 120, 43, 5_160),
    ("Office Chair", "Furniture", 100, 43, 4_300),
    ("Printer", "Electronics", 150, 19, 2_850),
    ("Keyboard", "Electronics", 50, 29, 1_450),
]

MONTHS = [("Jan", 73_500), ("Feb", 32_600), ("Mar", 6_500)]
DAYS = [
    ("Mon", 9_200),
    ("Tue", 29_590),
    ("Wed", 6_850),
    ("Thu", 25_200),
    ("Fri", 17_010),
    ("Sat", 16_950),
    ("Sun", 7_800),
]

# First 26 of the 50 records, transcribed from the published data extract.
# Dates are stored as ISO dates; the source workbook used Excel serial numbers.
TRANSACTIONS = [
    ("2024-01-25", "Thu", "West", "Michael Brown", "Smartphone", "Electronics", 13, 500, 6_500),
    ("2024-01-15", "Mon", "East", "Michael Brown", "Monitor", "Electronics", 14, 250, 3_500),
    ("2024-01-26", "Fri", "West", "John Doe", "Office Chair", "Furniture", 1, 100, 100),
    ("2024-02-06", "Tue", "East", "Jane Smith", "Desk", "Furniture", 3, 200, 600),
    ("2024-02-07", "Wed", "West", "John Doe", "Printer", "Electronics", 9, 150, 1_350),
    ("2024-01-30", "Tue", "East", "Jane Smith", "Laptop", "Electronics", 10, 700, 7_000),
    ("2024-01-20", "Sat", "North", "Emily Davis", "Laptop", "Electronics", 11, 700, 7_700),
    ("2024-01-05", "Fri", "South", "Jane Smith", "Smartphone", "Electronics", 1, 500, 500),
    ("2024-02-27", "Tue", "South", "John Doe", "Desk", "Furniture", 10, 200, 2_000),
    ("2024-01-06", "Sat", "West", "Emily Davis", "Printer", "Electronics", 6, 150, 900),
    ("2024-02-13", "Tue", "North", "Emily Davis", "Bookshelf", "Furniture", 4, 120, 480),
    ("2024-01-24", "Wed", "West", "Michael Brown", "Keyboard", "Electronics", 14, 50, 700),
    ("2024-03-01", "Fri", "East", "Michael Brown", "Smartphone", "Electronics", 6, 500, 3_000),
    ("2024-01-16", "Tue", "West", "Chris Taylor", "Bookshelf", "Furniture", 12, 120, 1_440),
    ("2024-02-05", "Mon", "South", "Jane Smith", "Keyboard", "Electronics", 9, 50, 450),
    ("2024-03-01", "Fri", "North", "John Doe", "Laptop", "Electronics", 5, 700, 3_500),
    ("2024-02-19", "Mon", "South", "Jane Smith", "Smartphone", "Electronics", 2, 500, 1_000),
    ("2024-01-02", "Tue", "West", "Michael Brown", "Tablet", "Electronics", 9, 300, 2_700),
    ("2024-01-23", "Tue", "East", "Michael Brown", "Laptop", "Electronics", 15, 700, 10_500),
    ("2024-01-01", "Mon", "East", "John Doe", "Office Chair", "Furniture", 10, 100, 1_000),
    ("2024-02-04", "Sun", "North", "John Doe", "Laptop", "Electronics", 9, 700, 6_300),
    ("2024-01-22", "Mon", "North", "Michael Brown", "Office Chair", "Furniture", 3, 100, 300),
    ("2024-01-18", "Thu", "South", "John Doe", "Bookshelf", "Furniture", 12, 120, 1_440),
    ("2024-02-20", "Tue", "South", "Emily Davis", "Printer", "Electronics", 1, 150, 150),
    ("2024-02-23", "Fri", "South", "Jane Smith", "Office Chair", "Furniture", 6, 100, 600),
    ("2024-02-08", "Thu", "South", "John Doe", "Headphones", "Electronics", 12, 80, 960),
]


def check(label: str, value: float, expected: float) -> None:
    if round(value, 2) != round(expected, 2):
        raise SystemExit(f"Reconciliation failed for {label}: {value} != {expected}")


def main() -> None:
    DATA.mkdir(exist_ok=True)

    # --- Region -------------------------------------------------------------
    units_by_region = {
        "East": sum(r[1] for r in UNITS_MATRIX),
        "North": sum(r[2] for r in UNITS_MATRIX),
        "South": sum(r[3] for r in UNITS_MATRIX),
        "West": sum(r[4] for r in UNITS_MATRIX),
    }
    region = pd.DataFrame(
        [
            {
                "region": name,
                "revenue": rev,
                "units_sold": units_by_region[name],
                "revenue_per_unit": round(rev / units_by_region[name], 2),
                "revenue_share_pct": round(rev / TOTAL_REVENUE * 100, 2),
            }
            for name, rev in REGIONS
        ]
    ).sort_values("revenue", ascending=False)
    check("region revenue", region["revenue"].sum(), TOTAL_REVENUE)
    check("region units", region["units_sold"].sum(), TOTAL_UNITS)
    region.to_csv(DATA / "revenue_by_region.csv", index=False)

    # --- Salesperson --------------------------------------------------------
    units_by_person = {row[0]: sum(row[1:]) for row in UNITS_MATRIX}
    sales = pd.DataFrame(
        [
            {
                "salesperson": name,
                "revenue": rev,
                "units_sold": units_by_person[name],
                "revenue_per_unit": round(rev / units_by_person[name], 2),
                "revenue_share_pct": round(rev / TOTAL_REVENUE * 100, 2),
            }
            for name, rev in SALESPEOPLE
        ]
    ).sort_values("revenue", ascending=False)
    check("salesperson revenue", sales["revenue"].sum(), TOTAL_REVENUE)
    check("salesperson units", sales["units_sold"].sum(), TOTAL_UNITS)
    sales.to_csv(DATA / "revenue_by_salesperson.csv", index=False)

    # --- Units by region and salesperson ------------------------------------
    matrix = pd.DataFrame(
        [
            {
                "salesperson": row[0],
                "East": row[1],
                "North": row[2],
                "South": row[3],
                "West": row[4],
                "total_units": sum(row[1:]),
            }
            for row in UNITS_MATRIX
        ]
    ).sort_values("total_units", ascending=False)
    matrix.to_csv(DATA / "units_by_region_and_salesperson.csv", index=False)

    # --- Product ------------------------------------------------------------
    product = pd.DataFrame(
        [
            {
                "product": name,
                "category": cat,
                "unit_price": price,
                "units_sold": units,
                "revenue": rev,
                "revenue_share_pct": round(rev / TOTAL_REVENUE * 100, 2),
            }
            for name, cat, price, units, rev in PRODUCTS
        ]
    ).sort_values("revenue", ascending=False)
    check("product revenue", product["revenue"].sum(), TOTAL_REVENUE)
    check("product units", product["units_sold"].sum(), TOTAL_UNITS)
    # Guard internal consistency: units x unit price must equal reported revenue.
    product["_implied"] = product["units_sold"] * product["unit_price"]
    mismatched = product[product["_implied"] != product["revenue"]]
    if not mismatched.empty:
        raise SystemExit(f"Unit price x units mismatch: {mismatched[['product']].to_dict()}")
    product = product.drop(columns="_implied")
    product.to_csv(DATA / "revenue_by_product.csv", index=False)

    # --- Category -----------------------------------------------------------
    category = (
        product.groupby("category", as_index=False)
        .agg(revenue=("revenue", "sum"), units_sold=("units_sold", "sum"), products=("product", "count"))
        .sort_values("revenue", ascending=False)
    )
    category["revenue_share_pct"] = (category["revenue"] / TOTAL_REVENUE * 100).round(2)
    check("category revenue", category["revenue"].sum(), TOTAL_REVENUE)
    category.to_csv(DATA / "revenue_by_category.csv", index=False)

    # --- Time ---------------------------------------------------------------
    month = pd.DataFrame(MONTHS, columns=["month", "revenue"])
    month["revenue_share_pct"] = (month["revenue"] / TOTAL_REVENUE * 100).round(2)
    check("monthly revenue", month["revenue"].sum(), TOTAL_REVENUE)
    month.to_csv(DATA / "revenue_by_month.csv", index=False)

    day = pd.DataFrame(DAYS, columns=["day", "revenue"])
    day["revenue_share_pct"] = (day["revenue"] / TOTAL_REVENUE * 100).round(2)
    check("daily revenue", day["revenue"].sum(), TOTAL_REVENUE)
    day.to_csv(DATA / "revenue_by_day.csv", index=False)

    # --- Transaction sample -------------------------------------------------
    transactions = pd.DataFrame(
        TRANSACTIONS,
        columns=[
            "date",
            "day",
            "region",
            "salesperson",
            "product",
            "category",
            "units_sold",
            "unit_price",
            "total_sales",
        ],
    )
    transactions["line_check"] = transactions["units_sold"] * transactions["unit_price"]
    if (transactions["line_check"] != transactions["total_sales"]).any():
        raise SystemExit("Transaction sample contains lines where units x price != total sales")
    transactions = transactions.drop(columns="line_check")
    transactions.to_csv(DATA / "transactions_sample.csv", index=False)

    print("All tables reconcile to $112,600 revenue and 420 units.")
    print(f"Transaction sample: {len(transactions)} records, "
          f"${transactions['total_sales'].sum():,.0f} revenue, "
          f"{transactions['units_sold'].sum():,} units")


if __name__ == "__main__":
    main()
