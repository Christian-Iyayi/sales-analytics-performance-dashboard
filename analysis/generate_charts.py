"""Regenerate every figure used in the README and report.

Charts are written to ``charts/`` as high-resolution PNGs, using the same
green palette as the original Excel dashboard so the repository visuals and the
source workbook read as one family.

Run from the repository root:

    python analysis/generate_charts.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CHARTS = ROOT / "charts"

# --- Palette ----------------------------------------------------------------
DARK = "#14391F"
PRIMARY = "#2E7D32"
MID = "#4CAF50"
LEAF = "#8BC34A"
LIGHT = "#C8E6C9"
ACCENT = "#E8A33D"
GRID = "#DDE3DD"
TEXT = "#2B3A31"
MUTED = "#6B7A70"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "text.color": TEXT,
        "axes.labelcolor": TEXT,
        "axes.edgecolor": GRID,
        "axes.titlecolor": DARK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "text.parse_math": False,
    }
)

USD = FuncFormatter(lambda x, _: f"${x:,.0f}")


def clean_axes(ax, grid_axis: str = "y") -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8, alpha=0.9)
    ax.set_axisbelow(True)


def titles(ax, title: str, subtitle: str | None = None) -> None:
    ax.set_title(title, fontsize=16, fontweight="bold", loc="left", pad=34 if subtitle else 12)
    if subtitle:
        ax.annotate(
            subtitle,
            xy=(0, 1.008),
            xycoords="axes fraction",
            fontsize=10.5,
            color=MUTED,
            ha="left",
            va="bottom",
        )


def footer(fig, text: str) -> None:
    fig.text(0.01, 0.012, text, fontsize=8.5, color=MUTED, ha="left")


def save(fig, name: str) -> None:
    CHARTS.mkdir(exist_ok=True)
    path = CHARTS / name
    fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.35)
    plt.close(fig)
    print("wrote", path.relative_to(ROOT))


SOURCE = "Source: Sales Analytics Performance Dashboard, Q1 2024 (50 records, $112,600 revenue)."


# --- Charts -----------------------------------------------------------------
def chart_region() -> None:
    df = pd.read_csv(DATA / "revenue_by_region.csv").sort_values("revenue")
    fig, ax = plt.subplots(figsize=(10, 5.2))
    colors = [LIGHT, LEAF, MID, PRIMARY]
    bars = ax.barh(df["region"], df["revenue"], color=colors, height=0.62)
    for bar, rev, share, rpu in zip(bars, df["revenue"], df["revenue_share_pct"], df["revenue_per_unit"]):
        ax.text(
            rev + 900,
            bar.get_y() + bar.get_height() / 2,
            f"${rev:,.0f}   ({share:.1f}%)   ${rpu:,.0f}/unit",
            va="center",
            fontsize=10.5,
            color=TEXT,
        )
    ax.set_xlim(0, 46_000)
    ax.xaxis.set_major_formatter(USD)
    clean_axes(ax, "x")
    titles(ax, "Revenue by region", "East and North deliver 60.7% of total revenue; South trails on both value and mix")
    footer(fig, SOURCE)
    save(fig, "01-revenue-by-region.png")


def chart_salespeople() -> None:
    df = pd.read_csv(DATA / "revenue_by_salesperson.csv").sort_values("revenue")
    fig, ax = plt.subplots(figsize=(10, 5.4))
    colors = [LIGHT] * len(df)
    colors[-1] = PRIMARY
    bars = ax.barh(df["salesperson"], df["revenue"], color=colors, height=0.6)
    for bar, rev, units, share in zip(bars, df["revenue"], df["units_sold"], df["revenue_share_pct"]):
        ax.text(
            rev + 700,
            bar.get_y() + bar.get_height() / 2,
            f"${rev:,.0f}   ({share:.1f}%)   {units} units",
            va="center",
            fontsize=10.5,
            color=TEXT,
        )
    ax.set_xlim(0, 52_000)
    ax.xaxis.set_major_formatter(USD)
    clean_axes(ax, "x")
    titles(ax, "Revenue by salesperson", "Michael Brown alone contributes 35.2% of quarterly revenue")
    footer(fig, SOURCE)
    save(fig, "02-revenue-by-salesperson.png")


def chart_revenue_per_unit() -> None:
    df = pd.read_csv(DATA / "revenue_by_salesperson.csv").sort_values("revenue_per_unit")
    fig, ax = plt.subplots(figsize=(10, 5.2))
    colors = [LIGHT] * len(df)
    colors[-1] = ACCENT
    bars = ax.barh(df["salesperson"], df["revenue_per_unit"], color=colors, height=0.6)
    for bar, rpu, units in zip(bars, df["revenue_per_unit"], df["units_sold"]):
        ax.text(
            rpu + 7,
            bar.get_y() + bar.get_height() / 2,
            f"${rpu:,.2f}/unit   ({units} units)",
            va="center",
            fontsize=10.5,
            color=TEXT,
        )
    ax.set_xlim(0, 480)
    ax.xaxis.set_major_formatter(USD)
    clean_axes(ax, "x")
    titles(
        ax,
        "Revenue per unit by salesperson",
        "Emily Davis earns 1.45x the team average per unit on a premium mix; John Doe sits at the bottom",
    )
    ax.axvline(268.10, color=MUTED, linestyle="--", linewidth=1.2)
    ax.annotate(
        "team average $268.10",
        xy=(268.10, len(df) - 0.35),
        xytext=(276, len(df) - 0.45),
        fontsize=9,
        color=MUTED,
    )
    footer(fig, SOURCE)
    save(fig, "03-revenue-per-unit-by-salesperson.png")


def chart_product() -> None:
    df = pd.read_csv(DATA / "revenue_by_product.csv").sort_values("revenue")
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    colors = [PRIMARY if c == "Electronics" else LEAF for c in df["category"]]
    bars = ax.barh(df["product"], df["revenue"], color=colors, height=0.62)
    for bar, rev, units in zip(bars, df["revenue"], df["units_sold"]):
        ax.text(
            rev + 700,
            bar.get_y() + bar.get_height() / 2,
            f"${rev:,.0f}   ({units} units)",
            va="center",
            fontsize=10,
            color=TEXT,
        )
    ax.set_xlim(0, 53_000)
    ax.xaxis.set_major_formatter(USD)
    clean_axes(ax, "x")
    titles(ax, "Revenue by product", "Laptop and Smartphone carry 60.1% of revenue between them")
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=PRIMARY),
        plt.Rectangle((0, 0), 1, 1, color=LEAF),
    ]
    ax.legend(handles, ["Electronics", "Furniture"], frameon=False, loc="lower right", fontsize=10)
    footer(fig, SOURCE)
    save(fig, "04-revenue-by-product.png")


def chart_category() -> None:
    df = pd.read_csv(DATA / "revenue_by_category.csv")
    fig = plt.figure(figsize=(10.6, 5.4))
    ax = fig.add_axes([0.03, 0.06, 0.40, 0.76])
    wedges, _ = ax.pie(
        df["revenue"].tolist(),
        colors=[PRIMARY, LEAF],
        startangle=90,
        counterclock=False,
        radius=1.0,
        wedgeprops=dict(width=0.34, edgecolor="white", linewidth=3),
    )
    ax.text(0, 0.09, "$112,600", ha="center", va="center", fontsize=19,
            fontweight="bold", color=DARK)
    ax.text(0, -0.17, "total revenue", ha="center", va="center", fontsize=10, color=MUTED)
    ax.set_aspect("equal")

    labels = [
        f"{row.category}\n${row.revenue:,.0f}  •  {row.revenue_share_pct:.2f}%  •  {row.units_sold} units"
        for row in df.itertuples()
    ]
    fig.legend(
        wedges,
        labels,
        loc="center left",
        bbox_to_anchor=(0.44, 0.42),
        frameon=False,
        fontsize=12,
        labelspacing=2.4,
        handlelength=1.1,
    )
    fig.text(0.03, 0.94, "Revenue mix by category", fontsize=17, fontweight="bold", color=DARK)
    fig.text(0.03, 0.885, "Electronics concentration is both the core strength and the main risk",
             fontsize=10.5, color=MUTED)
    footer(fig, SOURCE)
    save(fig, "05-revenue-mix-by-category.png")


def chart_month() -> None:
    df = pd.read_csv(DATA / "revenue_by_month.csv")
    fig, ax = plt.subplots(figsize=(9.5, 5))
    bars = ax.bar(df["month"], df["revenue"], color=[PRIMARY, MID, LIGHT], width=0.55)
    for bar, rev, share in zip(bars, df["revenue"], df["revenue_share_pct"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            rev + 1_800,
            f"${rev:,.0f}\n{share:.1f}%",
            ha="center",
            va="bottom",
            fontsize=10.5,
            color=TEXT,
        )
    ax.set_ylim(0, 86_000)
    ax.yaxis.set_major_formatter(USD)
    clean_axes(ax)
    titles(ax, "Revenue by month", "January accounts for 65.3% of the quarter; March is thin at 5.8%")
    ax.set_ylabel("Revenue")
    footer(fig, SOURCE)
    save(fig, "06-revenue-by-month.png")


def chart_day() -> None:
    df = pd.read_csv(DATA / "revenue_by_day.csv")
    order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    df = df.set_index("day").loc[order].reset_index()
    fig, ax = plt.subplots(figsize=(9.5, 5))
    ax.plot(
        df["day"], df["revenue"], color=PRIMARY, linewidth=2.6, marker="o",
        markersize=9, markerfacecolor="white", markeredgewidth=2.4, zorder=3,
    )
    ax.fill_between(df["day"], df["revenue"], color=LIGHT, alpha=0.55, zorder=1)
    for i, row in enumerate(df.itertuples()):
        ax.annotate(
            f"${row.revenue:,.0f}",
            xy=(i, row.revenue),
            xytext=(0, 16),
            textcoords="offset points",
            ha="center",
            fontsize=10.5,
            color=TEXT,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none", alpha=0.85),
        )
    ax.set_ylim(0, 36_000)
    ax.yaxis.set_major_formatter(USD)
    clean_axes(ax)
    titles(
        ax,
        "Revenue by day of week",
        "Tuesday and Thursday carry 48.7% of the week; Monday and Sunday are the quietest days",
    )
    ax.set_ylabel("Revenue")
    footer(fig, SOURCE)
    save(fig, "07-revenue-by-day-of-week.png")


def chart_heatmap() -> None:
    df = pd.read_csv(DATA / "units_by_region_and_salesperson.csv")
    regions = ["East", "North", "South", "West"]
    matrix = df.set_index("salesperson")[regions]
    matrix = matrix.loc[matrix.sum(axis=1).sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(8.6, 4.9))
    im = ax.imshow(matrix.values, cmap="Greens", aspect="auto", vmin=0, vmax=matrix.values.max())
    ax.set_xticks(range(len(regions)), regions)
    ax.set_yticks(range(len(matrix)), matrix.index)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            value = matrix.values[i, j]
            color = "white" if value > matrix.values.max() * 0.55 else DARK
            ax.text(j, i, f"{value}", ha="center", va="center", fontsize=12,
                    color=color, fontweight="bold")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks(np.arange(-0.5, len(regions), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(matrix), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=3)
    ax.tick_params(which="minor", length=0)
    cbar = fig.colorbar(im, ax=ax, pad=0.02, fraction=0.035)
    cbar.set_label("Units sold", color=MUTED)
    cbar.outline.set_visible(False)
    titles(ax, "Units sold by salesperson and region",
           "Michael Brown dominates West (68 units); Emily Davis is almost entirely a North resource (38 of 63)")
    footer(fig, SOURCE)
    save(fig, "08-units-heatmap-salesperson-region.png")


def chart_overview() -> None:
    region = pd.read_csv(DATA / "revenue_by_region.csv").sort_values("revenue", ascending=False)
    sales = pd.read_csv(DATA / "revenue_by_salesperson.csv").sort_values("revenue", ascending=False)
    product = pd.read_csv(DATA / "revenue_by_product.csv").sort_values("revenue", ascending=False).head(5)
    category = pd.read_csv(DATA / "revenue_by_category.csv")

    fig = plt.figure(figsize=(15, 8.4))
    gs = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.24)

    ax1 = fig.add_subplot(gs[0, 0])
    bars = ax1.bar(region["region"], region["revenue"], color=[PRIMARY, MID, LEAF, LIGHT], width=0.6)
    for bar, rev in zip(bars, region["revenue"]):
        ax1.text(bar.get_x() + bar.get_width() / 2, rev + 800, f"${rev/1000:,.1f}k",
                 ha="center", fontsize=10, color=TEXT)
    ax1.set_ylim(0, 41_000)
    ax1.yaxis.set_major_formatter(USD)
    clean_axes(ax1)
    titles(ax1, "Revenue by region")

    ax2 = fig.add_subplot(gs[0, 1])
    bars = ax2.barh(sales["salesperson"][::-1], sales["revenue"][::-1],
                    color=[LIGHT] * 4 + [PRIMARY], height=0.6)
    for bar, rev in zip(bars, sales["revenue"][::-1]):
        ax2.text(rev + 700, bar.get_y() + bar.get_height() / 2, f"${rev/1000:,.1f}k",
                 va="center", fontsize=10, color=TEXT)
    ax2.set_xlim(0, 47_000)
    ax2.xaxis.set_major_formatter(USD)
    clean_axes(ax2, "x")
    titles(ax2, "Revenue by salesperson")

    ax3 = fig.add_subplot(gs[1, 0])
    bars = ax3.barh(product["product"][::-1], product["revenue"][::-1], color=PRIMARY, height=0.6)
    for bar, rev in zip(bars, product["revenue"][::-1]):
        ax3.text(rev + 600, bar.get_y() + bar.get_height() / 2, f"${rev:,.0f}",
                 va="center", fontsize=10, color=TEXT)
    ax3.set_xlim(0, 53_000)
    ax3.xaxis.set_major_formatter(USD)
    clean_axes(ax3, "x")
    titles(ax3, "Top 5 products by revenue")

    ax4 = fig.add_subplot(gs[1, 1])
    wedges, _ = ax4.pie(category["revenue"], colors=[PRIMARY, LEAF], startangle=90,
                        counterclock=False,
                        wedgeprops=dict(width=0.36, edgecolor="white", linewidth=3))
    ax4.text(0, 0.1, "81.83%", ha="center", va="center", fontsize=20, fontweight="bold", color=DARK)
    ax4.text(0, -0.16, "Electronics share", ha="center", va="center", fontsize=10, color=MUTED)
    ax4.legend(wedges, [f"{r.category}  ${r.revenue:,.0f}" for r in category.itertuples()],
               frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.06), fontsize=9.5)
    titles(ax4, "Revenue mix by category")

    fig.suptitle(
        "Sales Analytics Performance Dashboard  |  Q1 2024 overview",
        x=0.005, y=1.045, ha="left", fontsize=21, fontweight="bold", color=DARK,
    )
    fig.text(0.005, 0.982, "50 records  •  $112,600 revenue  •  420 units  •  Jan–Mar 2024",
             fontsize=11.5, color=MUTED, ha="left")
    footer(fig, SOURCE)
    save(fig, "00-executive-overview.png")


def main() -> None:
    chart_overview()
    chart_region()
    chart_salespeople()
    chart_revenue_per_unit()
    chart_product()
    chart_category()
    chart_month()
    chart_day()
    chart_heatmap()


if __name__ == "__main__":
    main()
